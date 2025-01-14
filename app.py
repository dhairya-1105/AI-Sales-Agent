import streamlit as st
import speech_recognition as sr
import requests
import tempfile
import numpy as np
import time
from sales_agent import SalesAgent
import os
from audio_recorder_streamlit import audio_recorder
import io
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
    if 'waiting_for_user' not in st.session_state:
        st.session_state.waiting_for_user = False
    if 'last_audio' not in st.session_state:
        st.session_state.last_audio = None

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    play_text_as_speech(welcome_message)
    st.session_state.waiting_for_user = True

def convert_audio_to_text(audio_bytes):
    try:
        # Save the audio bytes to a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
            # Write WAV header manually
            with wave.open(temp_wav.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(41000)  # Sample rate
                wav_file.writeframes(audio_bytes)

        # Initialize recognizer
        r = sr.Recognizer()
        
        # Read the temporary file
        with sr.AudioFile(temp_wav.name) as source:
            audio_data = r.record(source)
            
        # Delete temporary file
        os.unlink(temp_wav.name)
            
        # Convert speech to text
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error with the speech recognition service."
    except Exception as e:
        print(f"Error in convert_audio_to_text: {str(e)}")
        return "An error occurred while processing the audio."

def play_text_as_speech(text):
    def clean_text(text):
        text = text.replace('*', ' ').replace('−', '-')
        return ' '.join(text.split())
    
    def chunk_text(text, max_length=200):
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
    
    cleaned_text = clean_text(text)
    chunks = chunk_text(cleaned_text)
    
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
                print(f"Error with chunk: {chunk}")
                print(f"Error response: {response.text}")
                continue
            
            st.markdown(f'<audio src="data:audio/wav;base64,{response.content.hex()}" autoplay>',
                       unsafe_allow_html=True)
            
            # Small pause between chunks
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing chunk: {chunk}")
            print(f"Error: {str(e)}")
            continue

def main():
    st.title("AI Sales Assistant")
    initialize_session_state()
    
    if not st.session_state.conversation_started:
        if st.button("Start Conversation"):
            start_conversation()
            st.rerun()
    
    if st.session_state.conversation_started:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Show recorder
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="user",
            icon_size="6x",
            pause_threshold=2.0,
            sample_rate=41_000
        )
        
        # Check if we have new audio that's different from last processed audio
        if audio_bytes and audio_bytes != st.session_state.last_audio:
            st.session_state.last_audio = audio_bytes  # Update last processed audio
            
            text = convert_audio_to_text(audio_bytes)
            
            if text and text != "Sorry, I couldn't understand the audio." and text != "Sorry, there was an error with the speech recognition service." and text != "An error occurred while processing the audio.":
                # Add user message
                st.session_state.messages.append({"role": "user", "content": text})
                
                # Generate and display assistant response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    response = st.session_state.agent.generate_response(
                        text,
                        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                    )
                    message_placeholder.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    play_text_as_speech(response)
                
                # Check if conversation should end
                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
                
                st.rerun()
            elif text != st.session_state.messages[-1].get("content", ""):
                st.error(text)

if __name__ == "__main__":
    main()
