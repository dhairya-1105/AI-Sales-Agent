import streamlit as st
import speech_recognition as sr
import requests
import tempfile
import numpy as np
import time
from sales_agent import SalesAgent
import os
import wave

def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    # Convert welcome message to speech
    play_text_as_speech(welcome_message)

def record_audio():
    # Initialize recognizer
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.write("Listening... Click 'Stop Recording' when done speaking.")
        audio = r.listen(source)
        
    try:
        # Convert speech to text
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error with the speech recognition service."

def play_text_as_speech(text):
    import os
    import requests
    import streamlit as st
    import tempfile
    
    # Clean and chunk the text
    def clean_text(text):
        # Remove special characters and normalize whitespace
        text = text.replace('*', ' ').replace('−', '-')
        return ' '.join(text.split())
    
    def chunk_text(text, max_length=200):  # Adjust max_length if needed
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2Nzc5MDI4MGM0NDE1ODdhYjZlODEwM2UiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM1OTgzNzQ0LCJleHAiOjQ4OTE3NDM3NDR9._Rhof8jciBrL8FBN1rR8-qX8GJOlrKcg9fbMnJxRbXc",
        "Content-Type": "application/json"
    }
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into chunks
    chunks = chunk_text(cleaned_text)
    
    # Process each chunk
    for chunk in chunks:
        try:
            payload = {
                "text": chunk,
                "voice_id": "mithali",
                "add_wav_header": True,
                "sample_rate": 16000,
                "speed": 1
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                st.error(f"Error with chunk: {chunk}")
                st.error(f"Error response: {response.text}")
                continue
                
            # Save and play the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(response.content)
                temp_filename = temp_file.name

            # Streamlit's audio player
            st.audio(temp_filename, format="audio/wav")
            
            # Clean up
            os.remove(temp_filename)
            
        except Exception as e:
            st.error(f"Error processing chunk: {chunk}")
            st.error(f"Error: {str(e)}")
            continue


def main():
    st.title("AI Sales Assistant")
    initialize_session_state()
    
    # Add a start button if conversation hasn't started
    if not st.session_state.conversation_started:
        if st.button("Start Conversation"):
            start_conversation()
            st.rerun()
    
    # Show chat interface once conversation has started
    if st.session_state.conversation_started:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Audio recording controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Recording"):
                st.session_state.recording = True
                text = record_audio()
                
                if text and text != "Sorry, I couldn't understand the audio." and text != "Sorry, there was an error with the speech recognition service.":
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": text})
                    
                    with st.chat_message("user"): 
                        st.write(text)
                    
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        response = st.session_state.agent.generate_response(
                            text,
                            [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                        )
                        message_placeholder.write(response)
                        play_text_as_speech(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Check if conversation should end
                    if not st.session_state.agent.conversation_active:
                        time.sleep(2)
                        st.session_state.conversation_started = False
                else:
                    st.error(text)
                
                st.session_state.recording = False
                st.rerun()

if __name__ == "__main__":
    main()
