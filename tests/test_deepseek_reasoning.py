import unittest
from unittest.mock import MagicMock, Mock
from src.plugins.llm_providers.deepseek import DeepSeekProvider

class TestDeepSeekReasoning(unittest.TestCase):
    def setUp(self):
        # Patch OpenAI init to avoid real connection attempt during init
        with unittest.mock.patch('src.plugins.llm_providers.deepseek.OpenAI'):
            self.provider = DeepSeekProvider(api_key="fake-key")
            # Now mock the internal client used in chat_stream
            self.provider._client = MagicMock()

    def test_reasoning_content_stream(self):
        """Test that reasoning_content is correctly yielded as thinking process."""
        
        # Mock chunks simulating DeepSeek R1 response
        # Chunk 1: Reasoning start
        chunk1 = Mock()
        chunk1.choices = [Mock()]
        chunk1.choices[0].delta = Mock()
        chunk1.choices[0].delta.reasoning_content = "Thinking step 1"
        chunk1.choices[0].delta.content = None

        # Chunk 2: Reasoning continuation
        chunk2 = Mock()
        chunk2.choices = [Mock()]
        chunk2.choices[0].delta = Mock()
        chunk2.choices[0].delta.reasoning_content = "\nThinking step 2"
        chunk2.choices[0].delta.content = None

        # Chunk 3: Transition to content
        chunk3 = Mock()
        chunk3.choices = [Mock()]
        chunk3.choices[0].delta = Mock()
        chunk3.choices[0].delta.reasoning_content = None
        chunk3.choices[0].delta.content = "Here is the result."

        # Setup mock stream
        mock_stream = [chunk1, chunk2, chunk3]
        self.provider._client.chat.completions.create.return_value = mock_stream

        # Execute
        generator = self.provider.chat_stream("test prompt")
        results = list(generator)

        # Verify
        # Expected:
        # 1. "> **Thinking Process:**\n> " (Header)
        # 2. "Thinking step 1" (First reasoning chunk)
        # 3. "\n> Thinking step 2" (Second reasoning chunk, newline replaced)
        # 4. "\n\n---\n\n" (Separator)
        # 5. "Here is the result." (Content)
        
        self.assertIn("> **Thinking Process:**\n> ", results)
        self.assertIn("Thinking step 1", results)
        self.assertIn("\n> Thinking step 2", results)
        self.assertIn("\n\n---\n\n", results)
        self.assertIn("Here is the result.", results)
        
        print("\nUnit Test Passed: Reasoning content correctly formatted.")

if __name__ == '__main__':
    unittest.main()
