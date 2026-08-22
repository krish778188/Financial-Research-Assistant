import streamlit as st
import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import uuid

# 1. Page Config & Env Setup
st.set_page_config(page_title="Finance Assistant", page_icon="📈")
load_dotenv()

# 2. Define Tools
@tool
def get_stock_data(company: str) -> str:
    """Get stocks data of a company"""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company}&apikey={os.getenv("ALPHA_VANTAGE_API_KEY")}'
    r = requests.get(url)
    data = r.json()
    if "Error Message" in data:
        return f"Error: {data['Error Message']}"
    stocks_data = data.get("Time Series (Daily)", {})
    return f"stocks data of {company} : {stocks_data}"

@tool
def get_company_news(company: str) -> str:
    """Get news of a company for stock price"""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(
        query=f"latest news in {company}",
        search_depth="basic",
        max_results=3
    )
    
    results = response.get("results", [])
    if not results:
        return f"No news found for {company}"
    
    news_list = []
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")
        news_list.append(f"- {title}\n  🔗 {url}\n  📝 {snippet[:100]}...")
    
    return f"Latest news in {company}:\n\n" + "\n\n".join(news_list)

# 3. Cache the Agent Initialization
@st.cache_resource
def get_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.7,  
    )
    memory = MemorySaver()
    
    # Using standard LangChain create_agent with system prompt and checkpointer
    return create_agent(
        model=llm,
        tools=[get_stock_data, get_company_news],
        system_prompt="You are a helpful stock assistant.",
        checkpointer=memory
    )

agent = get_agent()
# 4. Dynamic Session & Sidebar
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Chat Controls")
    if st.button("➕ Start New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    st.caption("Starting a new chat resets the context window and token history.")
    st.markdown("---")
    st.markdown("👨‍💻 **Made by Krish,**")
    st.markdown("**Gen AI Engineer**")

# 5. UI & Chat Interface
st.title("📈 Personal Finance Assistant")
st.markdown("Ask me for real-time stock data and the latest market news!")

# Display previous chat messages in the UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Chat Input Loop
if prompt := st.chat_input("E.g., What is the latest news for Apple?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": st.session_state.session_id}}
        
        try:
            with st.spinner("Analyzing market data..."):
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=config
                )
                
                content = result["messages"][-1].content
                if isinstance(content, list):
                    bot_response = "".join(
                        block.get("text", "") if isinstance(block, dict) else str(block)
                        for block in content
                    )
                else:
                    bot_response = str(content)
                
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
                st.warning(
                    "⚠️ **Rate / Token Limit Exceeded:** You have hit the API request or token quota.\n\n"
                    "• Please wait ~20–60 seconds before retrying.\n"
                    "• Or click **'➕ Start New Chat'** in the sidebar to reset the session."
                )
            elif "context length" in error_str or "token" in error_str:
                st.warning(
                    "⚠️ **Context Window Full:** The current conversation history is too long.\n\n"
                    "Please click **'➕ Start New Chat'** in the sidebar to start a fresh conversation."
                )
            else:
                st.error(f"An error occurred: {e}")
