import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_assist import generate_outline, genre_prompt_prefix, get_memory_context

class TestAIAssist(unittest.TestCase):
    
    @patch('core.ai_assist.openai.ChatCompletion.create')
    @patch('core.ai_assist.get_memory_context')
    def test_generate_outline(self, mock_get_memory, mock_openai_create):
        # Setup mock returns
        mock_get_memory.return_value = {"characters": ["Hero"], "locations": ["Castle"]}
        mock_openai_create.return_value = {
            'choices': [{'message': {'content': 'Test outline'}}]
        }
        
        # Call the function
        result = generate_outline("Test prompt", "fantasy", "gpt-3.5-turbo", 0.5)
        
        # Assert the result
        self.assertEqual(result, "Test outline")
        
        # Verify the API was called with correct parameters
        mock_openai_create.assert_called_once()
        args, kwargs = mock_openai_create.call_args
        self.assertEqual(kwargs['model'], "gpt-3.5-turbo")
        self.assertEqual(kwargs['temperature'], 0.5)
        
    def test_genre_prompt_prefix(self):
        # Test different genres
        fantasy_prompt = genre_prompt_prefix("fantasy")
        self.assertIn("fantasy", fantasy_prompt)
        
        scifi_prompt = genre_prompt_prefix("science fiction")
        self.assertIn("science fiction", scifi_prompt)

if __name__ == '__main__':
    unittest.main()