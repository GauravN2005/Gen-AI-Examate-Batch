import time
import unittest

from app.cache import TTLCache


class TTLCacheTests(unittest.TestCase):
    def test_hit_miss_expiry_and_limit(self) -> None:
        cache = TTLCache(max_entries=2, ttl_seconds=0.02)
        cache.set("one", {"answer": "1"})
        cache.set("two", {"answer": "2"})
        self.assertEqual(cache.get("one")["answer"], "1")
        self.assertIsNone(cache.get("missing"))
        cache.set("three", {"answer": "3"})
        self.assertEqual(cache.size(), 2)
        time.sleep(0.03)
        self.assertIsNone(cache.get("one"))
        self.assertEqual(cache.size(), 0)

    def test_duplicate_keys_and_stats(self) -> None:
        cache = TTLCache(max_entries=10, ttl_seconds=1)
        cache.set("same", {"answer": "safe"})
        self.assertIsNotNone(cache.get("same"))
        cache.get("same")
        stats = cache.stats()
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 0)


if __name__ == "__main__":
    unittest.main()
