import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text(prompt: str, model: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 2000) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful writing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def genre_prompt_prefix(genre):
    return f"You are a writing assistant helping develop a {genre} novel. Suggest a structured outline with key moments, conflicts, and character development."

def generate_outline(prompt, genre="fantasy", model="gpt-4", temperature=0.7):
    context = get_memory_context()
    combined_context = "\n".join([
        f"{section.capitalize()}: {json.dumps(data, indent=2)}"
        for section, data in context.items()
    ])

    messages = [
        {"role": "system", "content": genre_prompt_prefix(genre)},
        {"role": "user", "content": f"Story Memory:\n{combined_context}"},
        {"role": "user", "content": f"Based on the story above, create an outline for the next chapter. Prompt: {prompt}"}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content


def generate_chapter_from_outline_split(outline, model="gpt-3.5-turbo", temperature=0.7, retries=2):
    """
    Generate a chapter by splitting it into 3 parts and then combining them.
    This helps overcome token limitations and ensures longer chapters.
    """
    full_chapter = ""
    
    try:
        # Generate Part 1
        prompt_part1 = f"""
        Based on this outline:
        {outline}
        
        Write PART 1 OF 3 of a chapter (approximately 1000 words). 
        Focus on the beginning of the chapter, introducing the scene and starting the action.
        """
        
        part1 = generate_text(prompt_part1, model=model, temperature=temperature)
        full_chapter += part1 + "\n\n"
        
        # Generate Part 2
        prompt_part2 = f"""
        Based on this outline:
        {outline}
        
        And continuing from this beginning:
        {part1[:500]}...
        
        Write PART 2 OF 3 of the chapter (approximately 1000 words).
        Focus on developing the middle of the chapter, advancing the plot and deepening character interactions.
        """
        
        part2 = generate_text(prompt_part2, model=model, temperature=temperature)
        full_chapter += part2 + "\n\n"
        
        # Generate Part 3
        prompt_part3 = f"""
        Based on this outline:
        {outline}
        
        And continuing from this middle section:
        {part2[-500:]}
        
        Write PART 3 OF 3 of the chapter (approximately 1000 words).
        Focus on concluding the chapter with resolution of immediate conflicts and setting up for the next chapter.
        """
        
        part3 = generate_text(prompt_part3, model=model, temperature=temperature)
        full_chapter += part3
        
        return full_chapter
        
    except Exception as e:
        if retries > 0:
            print(f"Error generating chapter: {str(e)}. Retrying... ({retries} attempts left)")
            print(f"[Progress] Retrying... ({retries} left)")  # Add this line for better visibility
            return generate_chapter_from_outline_split(outline, model, temperature, retries-1)
        else:
            raise Exception(f"Failed to generate chapter after multiple attempts: {str(e)}")

def get_next_chapter_number():
    """
    Determine the next chapter number by examining existing chapter files.
    Returns the next number in sequence.
    """
    os.makedirs("chapters", exist_ok=True)
    chapters = [f for f in os.listdir("chapters") if f.startswith("chapter_") and f.endswith(".md")]
    
    if not chapters:
        return 1
        
    # Extract numbers from filenames like chapter_001.md -> 1
    chapter_nums = []
    for chapter in chapters:
        try:
            # Extract the number part between "chapter_" and ".md"
            num_part = chapter.replace("chapter_", "").replace(".md", "")
            chapter_nums.append(int(num_part))
        except ValueError:
            # Skip files that don't have a valid number format
            continue
            
    if not chapter_nums:
        return 1
        
    return max(chapter_nums) + 1

def save_new_chapter(chapter_text):
    """
    Save a new chapter with automatic numbering.
    Returns the path to the saved file.
    """
    next_num = get_next_chapter_number()
    chapter_path = f"chapters/chapter_{next_num:03d}.md"
    
    os.makedirs("chapters", exist_ok=True)
    with open(chapter_path, "w", encoding="utf-8") as f:
        f.write(chapter_text)
        
    return chapter_path

def append_to_current(chapter_text):
    """
    Append the generated chapter to the current story file.
    Returns the path to the current story file.
    """
    current_file = "memory/current_chapter.txt"
    
    os.makedirs("memory", exist_ok=True)
    with open(current_file, "a", encoding="utf-8") as f:
        f.write("\n\n" + chapter_text)
        
    return current_file

def reset_current_chapter():
    """
    Reset the current chapter file by clearing its contents.
    Returns the path to the reset file.
    """
    current_file = "memory/current_chapter.txt"
    
    os.makedirs("memory", exist_ok=True)
    with open(current_file, "w", encoding="utf-8") as f:
        f.write("")
        
    return current_file

# Update the existing generate_chapter_from_outline function to use the split approach
def generate_chapter_from_outline(outline, model="gpt-3.5-turbo", temperature=0.7, min_words=3000):
    """
    Generate a chapter from an outline, ensuring it meets minimum word count.
    Uses the split approach for more reliable generation of longer content.
    """
    chapter = generate_chapter_from_outline_split(outline, model, temperature)
    
    # Check if we met the minimum word count
    word_count = len(chapter.split())
    if word_count < min_words:
        print(f"Chapter only has {word_count} words, which is less than the minimum {min_words}.")
        print("Generating additional content...")
        
        # Generate an extension to the chapter
        extension_prompt = f"""
        Continue this chapter:
        {chapter[-1000:]}
        
        Write an additional section (approximately 1000 words) to extend the chapter.
        """
        
        extension = generate_text(extension_prompt, model=model, temperature=temperature)
        chapter += "\n\n" + extension
    
    return chapter

def get_memory_context():
    context = {}
    memory_dir = "memory"
    characters_path = os.path.join(memory_dir, "characters.json")
    locations_path = os.path.join(memory_dir, "locations.json")

    try:
        with open(characters_path, "r") as f:
            context["characters"] = json.load(f)
    except:
        context["characters"] = []

    try:
        with open(locations_path, "r") as f:
            context["locations"] = json.load(f)
    except:
        context["locations"] = []

    return context


def get_next_chapter_path():
    """Get the path for the next chapter file with auto-incrementing number"""
    os.makedirs("chapters", exist_ok=True)
    chapters = sorted([f for f in os.listdir("chapters") if f.startswith("chapter_")])
    next_num = len(chapters) + 1
    return f"chapters/chapter_{next_num:03d}.md"

def append_to_current(chapter_text: str):
    """Append generated chapter text to the current chapter file"""
    os.makedirs("memory", exist_ok=True)
    current_file = os.path.join("memory", "current_chapter.txt")
    
    with open(current_file, "a", encoding="utf-8") as f:
        f.write("\n\n" + chapter_text)
    
    return current_file

def reset_current_chapter():
    """Reset the current chapter file"""
    os.makedirs("memory", exist_ok=True)
    current_file = os.path.join("memory", "current_chapter.txt")
    
    with open(current_file, "w", encoding="utf-8") as f:
        f.write("")
    
    return current_file

def save_new_chapter(chapter_text: str):
    """Save a new chapter to the next available chapter file"""
    path = get_next_chapter_path()
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(chapter_text)
    
    return path