class PatternMemory:
    def upsert(self, pattern, response): return "stub-id"
    def update_score(self, pattern_id, success, impact): pass
    def find_similar(self, pattern, top_n=3): return []
    def get_best_response(self, pattern): return None
    def get_all(self, limit=100): return []
