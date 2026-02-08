# 🏠 Real Estate Assistant (Arabic RAG-Powered Search)


## 🌟 Overview
Traditional real estate platforms (like Nawy, Aqarmap, or Dubizzle) often rely on rigid, multi-step filtering systems. This creates a friction point for non-technical users and older generations who find complex UIs overwhelming.

This project introduces a **"Google-style" natural language interface** for real estate. By leveraging **Retrieval-Augmented Generation (RAG)** and **Vector Search**, users can find their dream home by simply describing it in plain Arabic or English—bypassing tedious checkboxes and manual filters.


## 🚀 Live Demo
You can interact with the live application here:
👉 **[Launch Real Estate AI Assistant](https://real-estate-ai-assistant-ptmjeyufburhgeanwkvemv.streamlit.app/)**


## ✨ Key Features
* **Natural Language Search:** Move beyond checkboxes. Type *"Apartment in New Cairo under 5M with 3 bedrooms"* and get instant results.
* **Bilingual Optimization:** Advanced support for Arabic and English queries, specifically tuned for the Egyptian/MENA market nuances.
* **Semantic Matching:** If an exact match isn't found, the system utilizes vector similarity to suggest the 2–3 closest alternatives.
* **AI-Powered Comparisons:** The LLM provides a side-by-side feature analysis to assist in decision-making.
* **Live Data Pipeline:** Seamlessly integrates with **Airtable** to ensure listings are always up-to-date.

## 🛠️ Tech Stack
* **Backend:** FastAPI (Python)
* **LLM Framework:** LangChain / OpenAI (GPT-4o)
* **Vector Database:** MongoDB Atlas Vector Search
* **Embeddings:** OpenAI 
* **Data Source:** Airtable API
* **Hosting:** Render
* **Frontend:** Streamlit

## 🏗️ Architecture & Workflow
The application follows a modular RAG architecture designed for speed and scalability:

1.  **Ingestion (`/sync`):** Property data is fetched from Airtable, vectorized, and stored in **MongoDB Atlas**.
2.  **Retrieval (`/chat`):** When a user types a query, the **FastAPI** backend performs a semantic search to find listings that match the *intent*, not just keywords.
3.  **Augmentation:** The top matches are retrieved and fed into the LLM as context.
4.  **Generation:** The LLM generates a natural response in Arabic or English, explaining why these units match the user's specific lifestyle requirements.

