import os
from datetime import datetime
from core.memory import load_memory, save_memory

def write_chapter():
    chapter_title = input("Enter chapter title: ").strip().replace(" ", "_")
    content = input("Paste or type your chapter content:\n")

    filename = f"{chapter_title}.md"
    filepath = os.path.join("chapters", filename)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Chapter saved as {filepath}")

def summarize_chapter():
    summaries = load_memory("chapters_summary")
    title = input("Enter chapter title for the summary: ")
    summary = input("Enter a short summary of the chapter:\n")

    summaries.append({"title": title, "summary": summary, "date": str(datetime.now())})
    save_memory("chapters_summary", summaries)

    print("Chapter summary saved.")
