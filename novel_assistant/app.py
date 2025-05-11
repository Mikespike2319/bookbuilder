from core.chapter import write_chapter, summarize_chapter
from core.memory import load_memory, save_memory
from core.utils import display_memory_section

def edit_memory():
    section = input("What section to edit? (characters, locations, plot, themes): ").strip().lower()
    if section not in ["characters", "locations", "plot", "themes"]:
        print("Invalid section.")
        return

    memory = load_memory(section)

    if section == "plot":
        memory["main"] = input("Main plot: ")
        sub = input("Add a subplot (press enter to skip): ")
        if sub:
            memory["subplots"].append(sub)
    else:
        item = input("Enter a new item to add: ")
        memory.append(item)

    save_memory(section, memory)
    print(f"{section.capitalize()} updated.")

def view_memory():
    for section in ["characters", "locations", "plot", "themes", "chapters_summary"]:
        display_memory_section(section)

def main():
    while True:
        print("\nNovel Assistant Menu")
        print("1. Write a new chapter")
        print("2. Summarize & save chapter")
        print("3. Edit story memory")
        print("4. View current memory")
        print("5. Exit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            write_chapter()
        elif choice == "2":
            summarize_chapter()
        elif choice == "3":
            edit_memory()
        elif choice == "4":
            view_memory()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
