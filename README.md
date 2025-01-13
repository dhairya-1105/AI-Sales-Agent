# SalesGPT: AI-Powered Context-Aware Sales Calling Agent

SalesGPT is an innovative, context-aware AI sales agent designed to streamline customer interactions across multiple channels, including voice, email, SMS, and messaging platforms (WhatsApp, Telegram, WeChat, etc.). 

The agent intelligently adapts to different stages of a sales conversation and uses powerful tools, such as a product catalog for recommendations and an order creation system, to enhance the sales process. With integration into voice and web platforms, SalesGPT offers a seamless experience for customers and sales teams alike.

---

## 🌟 Vision

Our vision is to create the *best open-source AI Sales Agent* that helps businesses improve sales processes, enhance customer experiences, and minimize operational costs. We welcome collaboration and ideas for improving SalesGPT. Feel free to reach out to us to share your use cases or feedback!

---

## Features

### 🚀 Key Capabilities
- *Context-Aware Conversations*: 
  SalesGPT understands and adjusts its responses based on the stage of the sales conversation, such as introduction, qualification, needs analysis, solution presentation, objection handling, and closing.

- *Tool Integration*:
  - *Search Product Tool*: A RAG (Retrieval-Augmented Generation) system that fetches relevant product information based on user queries.
  - *Create Order Tool*: Captures order details, saves them in an SQLite database, and generates a unique order ID.
  - *End Tool*: Provides a friendly farewell message and gracefully ends the conversation.

- *Voice & Text Integration*:
  - Voice input using speech_recognition.
  - Text-to-speech output using the Smallest AI API.
  - Hosted as a web application via Streamlit.

- *Multi-Channel Support*:
  Works across voice calls, email, and messaging platforms such as SMS, WhatsApp, Telegram, and more.

- *Automated Sales Support*:
  Capable of handling real-time customer queries, providing tailored recommendations, and closing sales autonomously.

### 🛠️ Advanced Functionalities
- *Data-Driven Recommendations*:
  References a pre-defined product knowledge base, reducing hallucinations and ensuring accuracy.
  
- *Real-Time Order Processing*:
  Manages customer orders, stores product information, and generates order confirmations with unique IDs.

- *Rapid Pipeline Response*:
  Optimized for voice conversations with a <1s response time for speech-to-text, LLM inference, and text-to-speech.

---

## Architecture

1. *AI Engine*:
   - Built using LlamaIndex's Groq LLM, offering contextual and conversational intelligence.
   - Supports synchronous and asynchronous operations with low latency.

2. *Product Catalog Retrieval*:
   - Implements FAISS-based nearest neighbor searches.
   - Maps product embeddings to the original catalog for efficient querying.

3. *Order Management*:
   - Integrates SQLite for managing order data with fields like order ID, customer name, product details, and timestamps.

4. *Web Interface*:
   - Hosted on Streamlit for easy accessibility and intuitive interaction.

---

## Setup and Installation

### Prerequisites
- Python 3.8+
- API Keys:
  - Groq API for LLMs
  - Smallest AI API for text-to-speech
  - Jina Embeddings API for retrieval
- Libraries: Install the required dependencies using the requirements.txt.
