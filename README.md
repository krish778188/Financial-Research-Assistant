# 📈 Personal Financial Research Assistant

An AI-powered financial agent built to help users make informed investment decisions. This assistant leverages Google's Gemini LLM to autonomously route queries, fetch real-time quantitative stock data, and analyze qualitative market sentiment from the latest news headlines.

## 🚀 Features

*   **Quantitative Market Data:** Integrates the Alpha Vantage API to fetch historical and real-time stock prices (OHLCV).
*   **Market Sentiment Analysis:** Utilizes the Tavily Search API to pull the latest financial news and analyst reports.
*   **Autonomous Tool Calling:** Powered by LangChain, the agent intelligently decides when to pull numbers versus when to read the news based on the user's prompt.
*   **Interactive Web UI:** Features a clean, conversational interface built entirely in Python using Streamlit.

## 🛠️ Tech Stack

*   **Language:** Python
*   **LLM:** Google Gemini (`gemini-2.5-flash`)
*   **Framework:** LangChain (`langchain`, `langchain-google-genai`)
*   **Frontend:** Streamlit
*   **Data APIs:** Alpha Vantage, Tavily Search

## ⚙️ Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/finance-assistant.git](https://github.com/yourusername/finance-assistant.git)
cd finance-assistant
