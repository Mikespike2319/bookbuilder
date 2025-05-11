from core.memory import load_memory

def display_memory_section(section):
    print(f"\n--- {section.upper()} ---")
    data = load_memory(section)
    if isinstance(data, list):
        for item in data:
            print(f"- {item}")
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key.capitalize()}: {value}")
