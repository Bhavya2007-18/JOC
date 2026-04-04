from intelligence.fixer import FixEngine

engine = FixEngine()

print("=== EXECUTE TWEAK ===")
res = engine.execute_tweak("reduce_visual_effects")
print(res)

action_id = res.get("action_id")

print("\n=== HISTORY AFTER EXECUTION ===")
print(engine.store.get_all_actions())

print("\n=== REVERT ACTION ===")
revert_res = engine.revert_action(action_id)
print(revert_res)

print("\n=== HISTORY AFTER REVERT ===")
print(engine.store.get_all_actions())