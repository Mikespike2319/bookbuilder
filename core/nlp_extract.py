# core/nlp_extract.py
import spacy
import os
import json

nlp = spacy.load("en_core_web_sm")

def extract_entities_from_chapter(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    doc = nlp(text)

    characters = set()
    locations = set()

    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            characters.add(ent.text.strip())
        elif ent.label_ in ["GPE", "LOC"]:
            locations.add(ent.text.strip())

    return list(characters), list(locations)

def update_memory_with_entities(characters, locations):
    memory_dir = "memory"

    # Update characters
    char_path = os.path.join(memory_dir, "characters.json")
    try:
        with open(char_path, "r") as f:
            existing_chars = json.load(f)
    except:
        existing_chars = []

    for char in characters:
        if char not in existing_chars:
            existing_chars.append(char)

    with open(char_path, "w") as f:
        json.dump(existing_chars, f, indent=2)

    # Update locations
    loc_path = os.path.join(memory_dir, "locations.json")
    try:
        with open(loc_path, "r") as f:
            existing_locs = json.load(f)
    except:
        existing_locs = []

    for loc in locations:
        if loc not in existing_locs:
            existing_locs.append(loc)

    with open(loc_path, "w") as f:
        json.dump(existing_locs, f, indent=2)