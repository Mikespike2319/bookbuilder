def extract_themes_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a literary analyst. Extract the main themes from this text."},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    themes = response['choices'][0]['message']['content'].split('\n')
    return [theme.strip() for theme in themes if theme.strip()]