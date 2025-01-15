# ⭐ AI Sales Agent

Our *AI Sales Agent* is an innovative, context-aware agent designed to streamline customer interactions across text and voice channels.  
Our vision is to create a capable, open-source AI Sales Agent that helps businesses improve sales processes, enhance customer experiences, and minimize operational costs.  

Feel free to reach out to us to share your use cases or feedback!

---

## Features

### 🚀 Key Capabilities
- *Context-Aware Conversations*:  
  Understands and adjusts responses based on the sales stage (e.g., introduction, needs analysis, solution presentation, objection handling, and closing).

- *Tool Integration*:
  - Search Product Tool: Uses RAG (Retrieval-Augmented Generation) to fetch relevant product information based on user queries.
  - Create Order Tool: Captures order details, stores them in an SQLite database, and generates a unique order ID.
  - End Tool: Provides a friendly farewell message and gracefully ends the conversation.

- *Voice & Text Integration*:
  - Voice input using speech_recognition.
  - Text-to-speech output using the Smallest AI API.
  - Hosted as a web application via *Streamlit Cloud*.

- *Automated Sales Support*:  
  Handles real-time customer queries, provides tailored recommendations, and autonomously closes sales.

### 🛠 Advanced Functionalities
- *Data-Driven Recommendations*:  
  Uses a pre-defined product knowledge base to ensure accuracy and reduce hallucinations.

- *Real-Time Order Processing*:  
  Manages customer orders, stores product details, and generates unique order confirmations.

- *Rapid Pipeline Response*:  
  Optimized for voice conversations with a response time of under 2 seconds (speech-to-text, LLM inference, and text-to-speech).

---

## Architecture

1. *AI Engine*:  
   Built with *LlamaIndex's Groq LLM (llama-3.3-70b-versatile)* for contextual and conversational intelligence.  
   Supports synchronous and asynchronous operations with low latency.

2. *Product Catalog Retrieval*:  
   Implements FAISS-based nearest neighbor searches, mapping product embeddings to the catalog for efficient querying.

3. *Order Management*:  
   Integrates SQLite to manage order data with fields like:
   - Order ID
   - Customer Name
   - Product Details
   - Timestamp

4. *Web Interface*:  
   Hosted on *Streamlit* for easy accessibility and user-friendly interaction.

---
  
Access our Streamlit Cloud demo [here](https://ai-sales-agent-644hxadbndzatju8g27dbz.streamlit.app/)

*NOTE* : The speech-to-text API requires some warm-up time, so users are requested to wait a couple of seconds before clicking the mic button and give another second of pause after clicking the mic button to avoid problems with the STT.

Watch local demo [here](https://youtu.be/rwCstwRoIVQ)

---
## Chat Example
```
*Niharika*: Hello, my name is Niharika, and I'm a Business Representative from Sleep Victory. I'm calling today to introduce
our premium mattress company and see if we can help you achieve a better night's sleep. We specialize in providing
high-quality sleep solutions that can improve overall health and well-being. Can I take a minute to discuss how our products
 might benefit you?

*Tanish*: Hello Niharika, I am Tanish. I am really struggling with sleep issues lately; I guess now it's time for me to
change the mattress.

---

*Niharika*: I'm so glad you're considering a new mattress, Tanish. What kind of mattress are you currently using, and what
specific issues are you experiencing with your sleep?

*Tanish*: I have back pain; doctors have suggested me to use firm pillows under my waist.

---

*Niharika*: It sounds like you're experiencing some discomfort and back pain, and your doctor has recommended using firm
pillows for support. Have you considered a mattress with extra lumbar support or a firmer mattress to help alleviate your
back pain?

*Tanish*: Yeah, maybe, that sounds promising. Can you suggest some?

---

*Tool Used*: Search Catalog  
*Input*: Mattresses with extra lumbar support  
*Output*:  
- *Orthopedic Supreme Gel Memory Mattress: Provides precise pressure relief for joints and the spine. Designed for those
with orthopedic needs. Priced at *$1,799**.

*Niharika: I'd recommend the Orthopedic Supreme Gel Memory Mattress, which provides precise pressure relief for joints
and the spine. This mattress is designed for those with specific orthopedic needs and offers optimal firmness for posture
correction. It's priced at *$1,799**.

*Tanish*: Are there any cheaper options available, because currently, I am short on cash?

---

*Tool Used*: Search Catalog  
*Input*: Affordable mattresses with lumbar support  
*Output*:  
- *Classic Harmony Spring Mattress: Offers great support and a comfortable sleeping surface. It's firmer than some other
 options and priced at *$1,299**.

*Niharika*: I completely understand that budget can be a concern, Tanish. Let me see if I can find some more affordable
options for you with similar features. The *Classic Harmony Spring Mattress* offers great support and a comfortable sleeping
surface. It's a bit firmer and has a price tag of *$1,299*, which is under your budget. This might be a good fit for you
since it provides the lumbar support
you're looking for.

*Tanish*: Yeah, that's under my budget.

---

*Niharika*: I'm glad the Classic Harmony Spring Mattress fits within your budget, Tanish. Would you like to proceed with
purchasing this mattress, or would you like me to explore more options for you?

*Tanish*: I think this will be a good fit for me, Niharika.

---

*Tool Used*: Create Order  
*Input*: Classic Harmony Spring Mattress  
*Output*:  
- *Order ID*: 9d9b52b5-78be-44f2-b407-9b3fe4895cad

*Niharika*: I'm so glad you've found a mattress that you think will be a good fit for you, Tanish. To proceed with the purchase,
 I just need to confirm your name, which you've already provided.

---

*Tanish*: Thanks, Niharika.

*Niharika*: You're welcome, Tanish. It was a pleasure assisting you in finding a new mattress that should help with your back pain.
 If you have any other questions or need further assistance in the future, don't hesitate to reach out. Have a great day, and I hope
you enjoy your new mattress! Thanks so much for chatting with us, Tanish - we appreciate the time you
 took to talk with us.
```

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dhairya-1105/AI-Sales-Agent
cd AI-Sales-Agent
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Setup API Keys
Replace the API keys in the code with your own API keys. This includes Groq, Jina Embeddings, and Smallest.ai
### 4. Prepare Vector Database
Run the create_catalog.py file to generate a vector database of the sample catalog using Jina Embeddings
### 5. Launch the app
```bash
python app.py
```
