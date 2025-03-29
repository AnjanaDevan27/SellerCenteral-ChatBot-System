import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
from langchain.prompts import PromptTemplate
from Data.meta_data import fetch_metadata
from Data.user_review import fetch_reviews
from chain import create_qa_chain 
from retriever import create_retriever_from_df 
# Load environment variables from .env
load_dotenv()

# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def handle_user_input(user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_handle_user_input(user_input))

async def async_handle_user_input(user_input):
    answer = await qa_chain.ainvoke(user_input)
    return answer

# Set up the Streamlit page
st.set_page_config(page_title="Amazon Seller Central Chatbot", page_icon="🤖", layout="wide")
st.title("Amazon Seller Central Chatbot")
st.subheader("Your Intelligent Seller Companion")

# Input: Product ASIN
asin = st.text_input("Enter your product ASIN:", key="asin_input")

if asin:
    st.info("Fetching data from BigQuery...")
    review_df = fetch_reviews(asin)
    meta_df = fetch_metadata(asin)
    
    if review_df.empty:
        st.error("No review data found for the provided ASIN.")
    else:
        st.success("Data fetched successfully!")
        st.write("Sample Review Data:", review_df.head())
        st.write("Sample Metadata:", meta_df.head())

        system_prompt = (f''' You are a great Data Interpreter and a helpful AI assistant to help the sellers in Amazon eCommerce company. 
                        Read all the data sent to you. 
                         Please provide the most appropriate response based on the question'''
                        "{context}"
                        '''
                        Help user answer any question regarding the product. 
                        Just answer the questions in brief.

                        Your responses should be clear, concise, and insightful.
                        ''')
        PROMPT = PromptTemplate(template=system_prompt, input_variables=["context", "question"])
        retriever = create_retriever_from_df(review_df)
        # Create the QA chain using the retriever
        qa_chain = create_qa_chain(retriever)

        # Input: User question
        user_question = st.text_input("Ask a question about your product:", key="user_question")
        
        if user_question:
            st.info("Generating answer...")
            try:
                # Run the chain to generate an answer
                answer = qa_chain.invoke(user_question)
                st.markdown("**Answer:**")
                st.write(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")
        
        # Display conversation history
        st.markdown("### Conversation History")
        for msg in qa_chain.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                role = "User"
            elif isinstance(msg, AIMessage):
                role = "Assistant"
            elif isinstance(msg, SystemMessage):
                role = "System"
            else:
                role = "Unknown"
            content = msg.content
            st.write(f"**{role}:** {content}")
