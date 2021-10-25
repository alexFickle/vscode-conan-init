import unittest

from vscode_conan_init import _MacroDefinitions


class TestMacroDefinitions(unittest.TestCase):
    def test_new_empty(self):
        definitions = _MacroDefinitions()
        self.assertEqual(definitions.as_list(), [])

    def test_name_with_no_value(self):
        self.assertEqual(_MacroDefinitions._get_name("foo"), "foo")

    def test_name_with_value(self):
        self.assertEqual(_MacroDefinitions._get_name("foo=bar"), "foo")

    def test_add_new(self):
        definitions = _MacroDefinitions()
        self.assertEqual(None, definitions.add("foo=bar"))
        self.assertEqual(definitions.as_list(), ["foo=bar"])

    def test_add_overwrite(self):
        definitions = _MacroDefinitions()
        definitions.add("foo=bar")
        self.assertEqual(definitions.add("foo"), "foo=bar")
        self.assertEqual(definitions.as_list(), ["foo"])

    def test_remove_missing(self):
        definitions = _MacroDefinitions()
        self.assertEqual(definitions.remove("foo"), None)

    def test_remove_existing(self):
        definitions = _MacroDefinitions()
        definitions.add("foo=bar")
        self.assertEqual(definitions.remove("foo"), "foo=bar")
        self.assertEqual(definitions.as_list(), [])

    def test_as_list(self):
        definitions = _MacroDefinitions()
        definitions.add("a=1")
        definitions.add("c=2")
        definitions.add("b=3")
        self.assertEqual(definitions.as_list(), ["a=1", "b=3", "c=2"])


if __name__ == "__main__":
    unittest.main()
