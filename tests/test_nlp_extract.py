import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.nlp_extract import extract_entities_from_chapter, update_memory_with_entities

class TestNLPExtract(unittest.TestCase):
    
    @patch('core.nlp_extract.nlp')
    @patch('builtins.open', new_callable=mock_open, read_data="John went to New York.")
    def test_extract_entities(self, mock_file, mock_nlp):
        # Setup mock NLP processing
        mock_doc = MagicMock()
        mock_ent1 = MagicMock()
        mock_ent1.text = "John"
        mock_ent1.label_ = "PERSON"
        
        mock_ent2 = MagicMock()
        mock_ent2.text = "New York"
        mock_ent2.label_ = "GPE"
        
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc
        
        # Call the function
        characters, locations = extract_entities_from_chapter("test_chapter.md")
        
        # Assert the results
        self.assertEqual(characters, ["John"])
        self.assertEqual(locations, ["New York"])
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    @patch('os.path.join')
    def test_update_memory(self, mock_join, mock_json_dump, mock_json_load, mock_file):
        # Setup mocks
        mock_json_load.side_effect = [["Existing Character"], ["Existing Location"]]
        mock_join.side_effect = ["memory/characters.json", "memory/locations.json"]
        
        # Call the function
        update_memory_with_entities(["John", "Existing Character"], ["New York", "Existing Location"])
        
        # Check that json.dump was called with the updated lists
        calls = mock_json_dump.call_args_list
        self.assertEqual(len(calls), 2)
        
        # First call should be for characters
        args, _ = calls[0]
        self.assertEqual(set(args[0]), set(["Existing Character", "John"]))
        
        # Second call should be for locations
        args, _ = calls[1]
        self.assertEqual(set(args[0]), set(["Existing Location", "New York"]))

if __name__ == '__main__':
    unittest.main()