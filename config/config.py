import os
# Set API keys and tokens from environment variables
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
# os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ["DEEPSEEK_API_KEY"] = os.getenv('DEEPSEEK_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
os.environ['LANGFUSE_PUBLIC_KEY'] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ['LANGFUSE_SECRET_KEY'] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ['LANGFUSE_HOST'] = os.getenv("LANGFUSE_HOST")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set up BigQuery credentials; ensure GOOGLE_APPLICATION_CREDENTIALS points to your file
# For example, if using a file mounted in your container:
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')