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
## Chat Example
```diff
+ *Niharika*: Hello, my name is Niharika, and I'm a Business Representative from Sleep Victory. I'm calling today to introduce our premium mattress company and see if we can help you achieve a better night's sleep. We specialize in providing high-quality sleep solutions that can improve overall health and well-being. Can I take a minute to discuss how our products might benefit you?  
- *User*: Hello Niharika, I am Tanish. I am really struggling with sleep issues lately; I guess now it's time for me to change the mattress.  

---

+ *Niharika*: I'm so glad you're considering a new mattress, Tanish. What kind of mattress are you currently using, and what specific issues are you experiencing with your sleep?  
- *User*: I have back pain; doctors have suggested me to use firm pillows under my waist.  

---

+ *Niharika*: It sounds like you're experiencing some discomfort and back pain, and your doctor has recommended using firm pillows for support. Have you considered a mattress with extra lumbar support or a firmer mattress to help alleviate your back pain?  
- *User*: Yeah, maybe, that sounds promising. Can you suggest some?  

*Tool Called*: Search Catalog  
*Tool Input*: Mattresses with extra lumbar support  
*Tool Output*:  
- *Option 1: Orthopedic Supreme Gel Memory Mattress - Provides precise pressure relief for joints and the spine. Designed for those with orthopedic needs. Priced at *$1,799**.  

+ *Niharika: I'd recommend the Orthopedic Supreme Gel Memory Mattress, which provides precise pressure relief for joints and the spine. This mattress is designed for those with specific orthopedic needs and offers optimal firmness for posture correction. It's priced at *$1,799**.  

- *User*: Are there any cheaper options available, because currently, I am short on cash?  

---

*Tool Called*: Search Catalog  
*Tool Input*: Affordable mattresses with lumbar support  
*Tool Output*:  
- *Option 1: Classic Harmony Spring Mattress - Offers great support and a comfortable sleeping surface. It's firmer than some other options and priced at *$1,299**.  

+ *Niharika*: I completely understand that budget can be a concern, Tanish. Let me see if I can find some more affordable options for you with similar features.  
- *Option: The Classic Harmony Spring Mattress offers great support and a comfortable sleeping surface. It's a bit firmer and has a price tag of *$1,299**, which is under your budget. This might be a good fit for you since it provides the lumbar support you're looking for.  

- *User*: Yeah, that's under my budget.  

---

+ *Niharika*: I'm glad the Classic Harmony Spring Mattress fits within your budget, Tanish. Would you like to proceed with purchasing this mattress, or would you like me to explore more options for you?  
- *User*: I think this will be a good fit for me, Niharika.  

---

*Tool Called*: Create Order  
*Tool Input*: Classic Harmony Spring Mattress  
*Tool Output*:  
- *Order ID*: 9d9b52b5-78be-44f2-b407-9b3fe4895cad  

+ *Niharika*: I'm so glad you've found a mattress that you think will be a good fit for you, Tanish. To proceed with the purchase, I just need to confirm your name, which you've already provided.  

---

- *User*: Thanks, Niharika.  
+ *Niharika*: You're welcome, Tanish. It was a pleasure assisting you in finding a new mattress that should help with your back pain. If you have any other questions or need further assistance in the future, don't hesitate to reach out.  

+ *Niharika*: Have a great day, and I hope you enjoy your new mattress! Thanks so much for chatting with us, Tanish - we appreciate the time you took to talk with us.

## Setup and Installation

### Prerequisites
- Python 3.8+
- API Keys:
  - Groq API for LLMs
  - Smallest AI API for text-to-speech
  - Jina Embeddings API for retrieval
- Libraries: Install the required dependencies using the requirements.txt.
