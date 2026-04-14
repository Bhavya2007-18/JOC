from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot


def generate_cpu_spike_scenario() -> List[VirtualSnapshot]:
    # 10 deterministic steps: normal -> rising -> high CPU.
    cpu_series = [20.0, 25.0, 30.0, 40.0, 55.0, 70.0, 80.0, 86.0, 90.0, 95.0]
    chrome_cpu_series = [10.0, 15.0, 20.0, 35.0, 45.0, 55.0, 60.0, 65.0, 68.0, 70.0]
    code_cpu_series = [8.0, 8.0, 9.0, 10.0, 10.0, 11.0, 12.0, 12.0, 13.0, 13.0]
    system_cpu_series = [3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0]

    memory_series = [50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 60.0]
    disk_series = [30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 40.0]
    process_count_series = [110, 110, 111, 112, 112, 113, 114, 114, 115, 115]

    scenario: List[VirtualSnapshot] = []

    for idx in range(10):
        processes = [
            VirtualProcessInfo(
                name="chrome.exe",
                pid=1234,
                cpu_percent=chrome_cpu_series[idx],
                memory_percent=25.0,
            ),
            VirtualProcessInfo(
                name="code.exe",
                pid=2345,
                cpu_percent=code_cpu_series[idx],
                memory_percent=12.0,
            ),
            VirtualProcessInfo(
                name="system.exe",
                pid=1,
                cpu_percent=system_cpu_series[idx],
                memory_percent=5.0,
            ),
        ]

        scenario.append(
            VirtualSnapshot(
                cpu_percent=cpu_series[idx],
                memory_percent=memory_series[idx],
                disk_percent=disk_series[idx],
                process_count=process_count_series[idx],
                top_processes=processes,
            )
        )

    return scenario
