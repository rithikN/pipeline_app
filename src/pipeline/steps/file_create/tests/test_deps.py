import unittest

from pipeline.steps.file_create.utils.deps import dep_namespace, dep_category_key


class TestDeps(unittest.TestCase):
    def test_namespace_single(self):
        used = set()
        ns = dep_namespace({"namespace": "BLK"}, used=used)
        self.assertEqual(ns, "BLK")

    def test_namespace_multi_occurrence_suffix(self):
        used = set()
        ns1 = dep_namespace({"namespace": "BLK", "occurrence_total": 2, "occurrence_index": 1}, used=used)
        ns2 = dep_namespace({"namespace": "BLK", "occurrence_total": 2, "occurrence_index": 2}, used=used)
        self.assertEqual(ns1, "BLK_01")
        self.assertEqual(ns2, "BLK_02")

    def test_namespace_occurrence_index_zero_becomes_one(self):
        used = set()
        ns1 = dep_namespace({"namespace": "BLK", "occurrence_total": 2, "occurrence_index": 0}, used=used)
        self.assertEqual(ns1, "BLK_01")

    def test_namespace_collision_appends_counter(self):
        used = set()
        ns1 = dep_namespace({"namespace": "BLK"}, used=used)
        ns2 = dep_namespace({"namespace": "BLK"}, used=used)
        self.assertEqual(ns1, "BLK")
        self.assertEqual(ns2, "BLK__2")

    def test_category_key_prefers_asset_category_code(self):
        k = dep_category_key({"asset_category_code": "chr"})
        self.assertEqual(k, "CHR")

    def test_category_key_fallback_unknown(self):
        k = dep_category_key({})
        self.assertEqual(k, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()