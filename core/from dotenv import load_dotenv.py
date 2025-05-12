from dotenv import load_dotenv
load_dotenv(".env.txt")
openai.api_key = os.getenv("OPENAI_API_KEY")