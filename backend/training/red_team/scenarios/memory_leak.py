from typing import List

from training.red_team.virtual_snapshot import VirtualProcessInfo, VirtualSnapshot


def generate_memory_leak_scenario() -> List[VirtualSnapshot]:
    # 10 deterministic steps: moderate system -> sustained memory leak.
    memory_series = [40.0, 45.0, 50.0, 56.0, 63.0, 70.0, 78.0, 85.0, 90.0, 95.0]
    cpu_series = [24.0, 26.0, 28.0, 30.0, 31.0, 33.0, 34.0, 36.0, 37.0, 38.0]
    disk_series = [31.0, 31.0, 32.0, 32.0, 32.0, 33.0, 33.0, 33.0, 34.0, 34.0]
    process_count_series = [104, 106, 108, 111, 114, 117, 120, 123, 126, 129]

    # One leaking process: moderate CPU, memory grows from 10% to 65%.
    leaky_memory_series = [10.0, 12.0, 15.0, 19.0, 26.0, 35.0, 45.0, 54.0, 60.0, 65.0]
    leaky_cpu_series = [9.0, 10.0, 10.0, 11.0, 12.0, 12.0, 13.0, 14.0, 14.0, 15.0]

    # Other processes stay relatively stable to keep early steps non-dominant.
    code_memory_series = [9.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
    code_cpu_series = [8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.0]

    system_memory_series = [7.0, 7.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0, 8.0, 8.0]
    system_cpu_series = [4.0, 4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0]

    helper_memory_series = [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0]
    helper_cpu_series = [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]

    scenario: List[VirtualSnapshot] = []

    for idx in range(10):
        processes = [
            VirtualProcessInfo(
                name="leaky_app.exe",
                pid=4321,
                cpu_percent=leaky_cpu_series[idx],
                memory_percent=leaky_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="code.exe",
                pid=2345,
                cpu_percent=code_cpu_series[idx],
                memory_percent=code_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="system.exe",
                pid=1,
                cpu_percent=system_cpu_series[idx],
                memory_percent=system_memory_series[idx],
            ),
            VirtualProcessInfo(
                name="helper_service.exe",
                pid=7890,
                cpu_percent=helper_cpu_series[idx],
                memory_percent=helper_memory_series[idx],
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
