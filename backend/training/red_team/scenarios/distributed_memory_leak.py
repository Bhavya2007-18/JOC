from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot


def generate_distributed_memory_leak_scenario() -> List[VirtualSnapshot]:
    # 10 deterministic steps: distributed memory growth with no dominant process.
    memory_series = [50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 86.0, 91.0, 95.0]
    cpu_series = [22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0]
    disk_series = [30.0, 30.0, 31.0, 31.0, 32.0, 32.0, 33.0, 33.0, 34.0, 34.0]
    process_count_series = [112, 115, 118, 121, 124, 127, 130, 133, 136, 139]

    chrome_memory_series = [11.0, 12.0, 12.5, 13.0, 14.0, 15.0, 16.0, 17.0, 17.5, 18.0]
    code_memory_series = [10.0, 10.5, 11.0, 12.0, 12.5, 13.0, 14.0, 15.0, 15.5, 16.0]
    helper_memory_series = [9.0, 9.5, 10.0, 11.0, 11.5, 12.0, 13.0, 14.0, 14.5, 15.0]
    service_memory_series = [8.5, 9.0, 9.5, 10.0, 10.5, 11.5, 12.0, 13.0, 13.5, 14.0]
    background_memory_series = [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.5, 12.0, 12.5, 13.0]

    chrome_cpu_series = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
    code_cpu_series = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.0, 8.5]
    helper_cpu_series = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 7.5, 8.0]
    service_cpu_series = [4.0, 4.5, 5.0, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 7.5]
    background_cpu_series = [3.5, 4.0, 4.5, 5.0, 5.0, 5.5, 6.0, 6.5, 7.0, 7.0]

    scenario: List[VirtualSnapshot] = []

    for idx in range(10):
        processes = [
            VirtualProcessInfo(
                name="chrome.exe",
                pid=1234,
                cpu_percent=chrome_cpu_series[idx],
                memory_percent=chrome_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="code.exe",
                pid=2345,
                cpu_percent=code_cpu_series[idx],
                memory_percent=code_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="helper.exe",
                pid=3456,
                cpu_percent=helper_cpu_series[idx],
                memory_percent=helper_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="service.exe",
                pid=4567,
                cpu_percent=service_cpu_series[idx],
                memory_percent=service_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="background.exe",
                pid=5678,
                cpu_percent=background_cpu_series[idx],
                memory_percent=background_memory_series[idx],
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
