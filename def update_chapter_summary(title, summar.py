def update_chapter_summary(title, summary):
    summary_path = os.path.join("memory", "chapters_summary.json")
    try:
        with open(summary_path, "r") as f:
            summaries = json.load(f)
    except:
        summaries = []
    
    from datetime import datetime
    summaries.append({
        "title": title,
        "summary": summary,
        "date": str(datetime.now())
    })
    
    with open(summary_path, "w") as f:
        json.dump(summaries, f, indent=2)