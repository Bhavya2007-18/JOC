# Kernel / Driver Hooks — Experimental Research Notes
## ⚠️ ADVANCED / EXPERIMENTAL / NOT FOR PRODUCTION

### Why We Are NOT Building This
- Windows kernel drivers require EV (Extended Validation) code signing certificates
- Unsigned drivers cause BlueScreen on Windows 10/11 with Secure Boot enabled
- Kernel-mode bugs cause system crashes (BSOD), not application crashes
- Not required for hackathon scope — ETW covers OS-level telemetry safely

### Safe Alternatives (Already Implemented)
| Mechanism | Location in JOC | What It Captures |
|---|---|---|
| psutil | snapshot_provider.py | CPU, RAM, process list |
| ETW (User-Mode) | sensors/etw_adapter.py | Process events, disk IO |
| WMI | Future scope | Hardware inventory, driver info |
| Windows Perf Counters | Future scope | Low-level CPU counters |

### Future Exploration (Research Only)
- **eBPF on Windows**: Microsoft is adding eBPF support via `ebpf-for-windows` project
- **ETW Kernel Providers**: `Microsoft-Windows-Kernel-Process`, `Microsoft-Windows-Kernel-Disk`
  can be consumed from user-space with admin privileges — covered by etw_adapter.py
- **Sysmon**: Sysinternals tool that writes structured ETW events, zero driver risk

### References
- https://github.com/microsoft/ebpf-for-windows
- https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/event-tracing-for-windows--etw-
- https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
