# ai_agent.py
import os
from langchain.agents import AgentType, initialize_agent, tool
from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Pinecone
import pinecone
import requests

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SERP_API_KEY = os.environ.get("SERP_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
embedding_function = GoogleGenerativeAIEmbeddings(model_name="models/embedding-001", google_api_key=GOOGLE_API_KEY)

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index_name = "job-seeker-memory"

if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, dimension=768, metric="cosine")

vectorstore = Pinecone.from_existing_index(index_name, embedding_function)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

@tool
def get_job_trends(query: str) -> str:
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'organic_results' in data and data['organic_results']:
            return str(data['organic_results'][:3])
        else:
            return "No job trends found."
    except Exception as e:
        return f"Error retrieving job trends: {e}"

@tool
def get_salary_data(job_title: str, location: str) -> str:
    try:
        url = f"https://serpapi.com/search.json?q={job_title}+salary+{location}&api_key={SERP_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'organic_results' in data and data['organic_results']:
            return str(data['organic_results'][:3])
        else:
            return "Salary data not found."
    except Exception as e:
        return f"Error retrieving salary data: {e}"

@tool
def store_user_profile(career_field: str = None, preferred_location: str = None, job_preferences: str = None) -> str:
    data_to_store = f"Career Field: {career_field}, Location: {preferred_location}, Preferences: {job_preferences}"
    vectorstore.add_texts([data_to_store])
    return "User profile stored."

@tool
def retrieve_user_profile(query: str) -> str:
    retrieved_docs = vectorstore.similarity_search(query, k=2)
    profile_info = "\n".join([doc.page_content for doc in retrieved_docs])
    return profile_info or "No profile found."

tools = [get_job_trends, get_salary_data, store_user_profile, retrieve_user_profile]

agent_chain = initialize_agent(tools, llm, memory=memory, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True)

def run_agent(input_text: str):
    return agent_chain.run(input=input_text)

if __name__ == "__main__":
    print(run_agent("What are some in-demand skills in data analysis?"))
    print(run_agent("Store my career field as data science."))
    print(run_agent("What jobs should I consider?"))
