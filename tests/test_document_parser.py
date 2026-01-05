import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from document_parser import DocumentParser

class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        self.parser = DocumentParser()
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_txt(self):
        path = os.path.join(self.data_dir, 'test.txt')
        text = self.parser.parse_file(path)
        self.assertIn("This is a test text file.", text)

    def test_parse_md(self):
        path = os.path.join(self.data_dir, 'test.md')
        text = self.parser.parse_file(path)
        self.assertIn("This is a **markdown** file.", text)

    def test_parse_docx(self):
        path = os.path.join(self.data_dir, 'test.docx')
        text = self.parser.parse_file(path)
        self.assertIn("This is a test paragraph", text)

    def test_parse_pdf(self):
        path = os.path.join(self.data_dir, 'test.pdf')
        text = self.parser.parse_file(path)
        self.assertIn("This is a test PDF file", text)

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):
            self.parser.parse_file("test.xyz")

if __name__ == '__main__':
    unittest.main()
