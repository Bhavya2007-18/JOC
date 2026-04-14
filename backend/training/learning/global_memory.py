from training.learning.memory_store import UnifiedMemoryStore

memory = UnifiedMemoryStore()
memory.load()
print("Memory loaded:")
memory.print_memory()