from intelligence.tweaks.executor import execute_tweak, revert_tweak

print("=== APPLY TEST ===")
print(execute_tweak("reduce_visual_effects"))
print(execute_tweak("high_performance_mode"))

print("\n=== REVERT TEST ===")
print(revert_tweak("reduce_visual_effects"))
print(revert_tweak("high_performance_mode"))