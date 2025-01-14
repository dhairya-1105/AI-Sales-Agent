import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import requests
import tempfile
import os
import io
import numpy as np
import time
from sales_agent import SalesAgent

def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'audio_response_played' not in st.session_state:
        st.session_state.audio_response_played = False

def chunk_text(text, max_length=200):
    """Split text into chunks of maximum length while preserving word boundaries."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        # Add 1 to account for the space between words
        word_length = len(word) + 1
        if current_length + word_length > max_length and current_chunk:
            # Join current chunk and add to chunks
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    synthesize_speech(welcome_message)
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    st.session_state.audio_response_played = False

def synthesize_speech(text):
    # Only synthesize if not already played
    if not st.session_state.audio_response_played:
        # Clean the text
        text = ' '.join(text.replace('*', ' ').replace('−', '-').split())
        
        # Split text into chunks
        chunks = chunk_text(text, max_length=200)
        
        url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzdkNDZkNzcyZDk1YTBiMjZlMjI3ZWUiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM2MjYzMzgzLCJleHAiOjQ4OTIwMjMzODN9.vQSZlyYmkub1bBhjNghSD77Nt6HgVXK6hc62byFHbug",
            "Content-Type": "application/json"
        }
        
        try:
            for i, chunk in enumerate(chunks):
                payload = {
                    "text": chunk,
                    "voice_id": "mithali",
                    "add_wav_header": True,
                    "sample_rate": 16000,
                    "speed": 1
                }
                
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    st.audio(response.content, format='audio/wav')
                    # Add a small delay between chunks
                    if i < len(chunks) - 1:
                        time.sleep(0.5)
                else:
                    st.error(f"Failed to synthesize chunk {i+1}: {response.text}")
            
            st.session_state.audio_response_played = True
            
        except Exception as e:
            st.error(f"Error synthesizing speech: {str(e)}")

def process_audio(audio_bytes):
    if audio_bytes is None:
        return None
        
    # Create a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name
    
    try:
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Load the audio file
        with sr.AudioFile(temp_audio_path) as source:
            audio = r.record(source)
        
        # Convert speech to text
        text = r.recognize_google(audio)
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
        return text
    except sr.UnknownValueError:
        os.unlink(temp_audio_path)
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        os.unlink(temp_audio_path)
        return "Sorry, there was an error with the speech recognition service."
    except Exception as e:
        os.unlink(temp_audio_path)
        return f"An error occurred: {str(e)}"

def main():
    st.title("AI Sales Assistant")
    initialize_session_state()

    # Start button for conversation
    if not st.session_state.conversation_started:
        if st.button("Start Conversation"):
            start_conversation()

    # Show chat interface once the conversation starts
    if st.session_state.conversation_started:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Create a container for the audio recorder
        audio_container = st.container()
        
        with audio_container:
            st.write("Record your response below:")
            audio_bytes = audio_recorder(
                # pause_threshold=2.0,  # Increased pause threshold
                sample_rate=41000
            )

        # Reset audio_response_played when new recording starts
        if audio_bytes:
            st.session_state.audio_response_played = False
            
        # Handle recorded audio
        if audio_bytes:
            text = process_audio(audio_bytes)
            if text not in [None, "Sorry, I couldn't understand the audio.", "Sorry, there was an error with the speech recognition service."]:
                # Add user's message to chat history
                st.session_state.messages.append({"role": "user", "content": text})
                with st.chat_message("user"):
                    st.write(text)
                
                # Generate assistant's response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    response = st.session_state.agent.generate_response(
                        text,
                        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                    )
                    message_placeholder.write(response)
                    synthesize_speech(response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Check if conversation should end
                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
            else:
                st.error(text)

if __name__ == "__main__":
    main()
