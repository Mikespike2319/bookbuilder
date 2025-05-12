def generate_chapter_summary(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Create a concise summary of this chapter."},
            {"role": "user", "content": text}
        ],
        temperature=0.5,
        max_tokens=150
    )
    return response['choices'][0]['message']['content']