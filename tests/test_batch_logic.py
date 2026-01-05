import unittest
from unittest.mock import MagicMock
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from document_parser import DocumentParser
from resume_sniper import ResumeSniper

class TestBatchLogic(unittest.TestCase):
    def setUp(self):
        self.parser = DocumentParser()
        self.sniper = ResumeSniper()
        # Mock the actual LLM call
        self.sniper.analyze = MagicMock(return_value="# Mock Report")
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_batch_resumes(self):
        # Scenario: 1 JD, Multiple Resumes
        jd_text = "Target JD Content"
        resume_files = ['test.txt', 'test.md'] # Using existing test files as resumes
        
        results = {}
        for fname in resume_files:
            path = os.path.join(self.data_dir, fname)
            resume_text = self.parser.parse_file(path)
            report = self.sniper.analyze(resume_text, jd_text)
            results[fname] = report
        
        self.assertEqual(len(results), 2)
        self.assertEqual(self.sniper.analyze.call_count, 2)

    def test_batch_jds(self):
        # Scenario: 1 Resume, Multiple JDs
        resume_text = "Candidate Resume Content"
        jd_files = ['test.txt', 'test.md'] # Using existing test files as JDs
        
        results = {}
        for fname in jd_files:
            path = os.path.join(self.data_dir, fname)
            jd_text = self.parser.parse_file(path)
            report = self.sniper.analyze(resume_text, jd_text)
            results[fname] = report
            
        self.assertEqual(len(results), 2)
        self.assertEqual(self.sniper.analyze.call_count, 2)

if __name__ == '__main__':
    unittest.main()
