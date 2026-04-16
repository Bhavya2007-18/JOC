import threading
import time
import os
from collections import deque
from typing import List, Dict, Any
import psutil

class ETWAdapter:
    MAX_QUEUE = 50      # hard cap on buffered events
    MAX_PER_POLL = 25   # max events returned per poll() call

    def __init__(self):
        self._event_queue: deque = deque(maxlen=self.MAX_QUEUE)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._pid_cache: set = set()

        # Detect capabilities
        self._etw_lib    = self._detect_etw_library()
        self._is_admin   = self._check_admin()
        self._etw_active = self._etw_lib is not None and self._is_admin

        # Always start psutil fallback
        self._start_psutil_thread()

        # Start ETW thread only if capable
        if self._etw_active:
            self._start_etw_thread()

    def _detect_etw_library(self) -> str | None:
        try:
            import etw; return "etw"
        except ImportError: pass
        try:
            import pywintrace; return "pywintrace"
        except ImportError: pass
        return None   # neither available

    def _check_admin(self) -> bool:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def _start_psutil_thread(self):
        self._pid_cache = {p.pid for p in psutil.process_iter(['pid'])}
        t = threading.Thread(target=self._psutil_loop, daemon=True, name="etw-psutil-fallback")
        t.start()

    def _psutil_loop(self):
        while not self._stop_event.is_set():
            try:
                current_pids = {p.pid for p in psutil.process_iter(['pid', 'name'])}
                new_pids  = current_pids - self._pid_cache
                gone_pids = self._pid_cache - current_pids

                for pid in new_pids:
                    try:
                        proc = psutil.Process(pid)
                        self._enqueue({
                            "type":      "process_start",
                            "pid":       pid,
                            "name":      proc.name(),
                            "timestamp": time.time(),
                            "metadata":  {"source": "psutil", "parent_pid": proc.ppid()}
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                for pid in gone_pids:
                    self._enqueue({
                        "type":      "process_stop",
                        "pid":       pid,
                        "name":      "unknown",
                        "timestamp": time.time(),
                        "metadata":  {"source": "psutil"}
                    })

                self._pid_cache = current_pids
            except Exception:
                pass   # never crash monitor loop from here

            self._stop_event.wait(5.0)   # poll every 5 seconds (not every tick)

    def _start_etw_thread(self):
        t = threading.Thread(target=self._etw_loop, daemon=True, name="etw-kernel-session")
        t.start()

    def _etw_loop(self):
        """Attempts real ETW session. On any error, marks ETW as unavailable silently."""
        try:
            if self._etw_lib == "etw":
                self._run_etw_session()
            elif self._etw_lib == "pywintrace":
                self._run_pywintrace_session()
        except Exception as e:
            # Log once and disable ETW — psutil fallback continues running
            self._etw_active = False

    def _run_etw_session(self):
        import etw
        # Microsoft-Windows-Kernel-Process provider
        # GUID: 22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716
        provider = etw.GUID("{22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716}")
        session  = etw.ETW(providers=[etw.ProviderInfo("Kernel-Process", provider)])

        def on_event(event_tuple):
            _header, event_data = event_tuple
            pid  = event_data.get("ProcessID", 0)
            name = event_data.get("ImageFileName", "unknown")
            if pid > 4:   # skip System/Idle
                self._enqueue({
                    "type":      "process_start",
                    "pid":       pid,
                    "name":      name,
                    "timestamp": time.time(),
                    "metadata":  {"source": "etw_kernel"}
                })

        with session:
            session.start(on_event)
            self._stop_event.wait()   # blocks until stop() is called

    def _run_pywintrace_session(self):
        # Fallback empty logic if you do not have pywintrace provider code handy 
        # (psutil covers the basic need)
        pass

    def _enqueue(self, event: dict):
        self._event_queue.append(event)   # deque auto-evicts oldest if maxlen hit

    def poll(self) -> List[Dict[str, Any]]:
        """Drain queue and return up to MAX_PER_POLL events."""
        result = []
        for _ in range(self.MAX_PER_POLL):
            if not self._event_queue:
                break
            result.append(self._event_queue.popleft())
        return result

    def stop(self):
        self._stop_event.set()
