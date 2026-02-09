import unittest

from pipeline.steps.file_create.utils.tokens import resolve_tokens_in_str, resolve_tokens


class TestTokens(unittest.TestCase):
    def test_brace_tokens(self):
        s = "HLD_{EP}_{SQ}_{SH}"
        out = resolve_tokens_in_str(s, {"EP": "EP101", "SQ": "SQ010", "SH": "SH010"})
        self.assertEqual(out, "HLD_EP101_SQ010_SH010")

    def test_dollar_tokens(self):
        s = "HLD_$EP_$SQ_$SH"
        out = resolve_tokens_in_str(s, {"EP": "EP101", "SQ": "SQ010", "SH": "SH010"})
        self.assertEqual(out, "HLD_EP101_SQ010_SH010")

    def test_missing_tokens_left_intact(self):
        s = "HLD_{MISSING}_X"
        out = resolve_tokens_in_str(s, {"EP": "EP101"})
        self.assertEqual(out, "HLD_{MISSING}_X")

    def test_nested_resolution(self):
        obj = {"path": "X/{EP}", "items": ["{SQ}", {"k": "$SH"}]}
        out = resolve_tokens(obj, {"EP": "EP101", "SQ": "SQ010", "SH": "SH010"})
        self.assertEqual(out["path"], "X/EP101")
        self.assertEqual(out["items"][0], "SQ010")
        self.assertEqual(out["items"][1]["k"], "SH010")


if __name__ == "__main__":
    unittest.main()