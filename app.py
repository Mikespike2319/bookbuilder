import os
import openai
from dotenv import load_dotenv

from core.ai_assist import generate_outline
from core.nlp_extract import extract_entities_from_chapter, update_memory_with_entities
from core.utils import get_float_input, get_yes_no_input, get_string_input

# Load API Key
load_dotenv(".env.txt")  # or rename .env.txt to .env and just use load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    # Ensure directories exist
    os.makedirs("chapters", exist_ok=True)
    os.makedirs("memory", exist_ok=True)
    
    while True:
        print("\n===== Novel Assistant CLI =====")
        print("1. Create new chapter (placeholder)")
        print("2. Edit existing chapter (placeholder)")
        print("3. View chapter (placeholder)")
        print("4. Add to memory (placeholder)")
        print("5. View memory (placeholder)")
        print("6. Generate AI-assisted outline")
        print("7. Analyze chapter and extract memory elements")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Feature coming soon: Create new chapter")
        elif choice == "2":
            print("Feature coming soon: Edit existing chapter")
        elif choice == "3":
            print("Feature coming soon: View chapter")
        elif choice == "4":
            print("Feature coming soon: Add to memory")
        elif choice == "5":
            print("Feature coming soon: View memory")
        elif choice == "6":
            try:
                user_prompt = input("What should this chapter be about?\n")
                genre = get_string_input("Genre (default = fantasy): ", "fantasy")
                model = get_string_input("Model (gpt-4 / gpt-3.5-turbo): ", "gpt-4")
                temperature = get_float_input("Creativity (temperature, 0.0–1.0, default = 0.7): ", 0.0, 1.0, 0.7)

                outline = generate_outline(user_prompt, genre=genre, model=model, temperature=temperature)
                print("\n--- AI-Generated Chapter Outline ---\n")
                print(outline)

                if get_yes_no_input("\nDo you want to save this outline to chapters/? (y/n): "):
                    title = input("Enter a filename (no spaces): ").strip().replace(" ", "_")
                    with open(f"chapters/{title}_outline.md", "w") as f:
                        f.write(outline)
                    print(f"Outline saved as chapters/{title}_outline.md")
            except Exception as e:
                print(f"Error generating outline: {str(e)}")
                print("This could be due to an API issue, network problem, or invalid parameters.")

        elif choice == "7":
            try:
                filename = input("Enter the name of the chapter file to analyze (no path): ").strip()
                path = os.path.join("chapters", filename)

                if not os.path.exists(path):
                    print("File not found.")
                else:
                    characters, locations = extract_entities_from_chapter(path)
                    print(f"\nCharacters Found: {characters}")
                    print(f"Locations Found: {locations}")

                    if get_yes_no_input("Update memory files with these? (y/n): "):
                        update_memory_with_entities(characters, locations)
                        print("Memory updated successfully.")
            except Exception as e:
                print(f"Error analyzing chapter: {str(e)}")
                print("This could be due to an issue with spaCy or the file format.")

        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 0 and 7.")

if __name__ == "__main__":
    main()