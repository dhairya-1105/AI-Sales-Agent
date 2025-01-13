import streamlit as st
import requests
import speech_recognition as sr
import tempfile
import os
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
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None

def start_conversation():
    st.session_state.agent = SalesAgent(api_key=st.secrets["GROQ_API_KEY"])
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    
    # Optional: Text-to-speech for welcome message
    if play_text_as_speech(welcome_message):
        st.audio("temp_audio.wav")

def play_text_as_speech(text):
    try:
        url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
        headers = {
            "Authorization": "Bearer " + st.secrets["WAVES_API_KEY"],
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_id": "mithali",
            "add_wav_header": True,
            "sample_rate": 16000,
            "speed": 1
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Save audio temporarily
            with open('temp_audio.wav', 'wb') as f:
                f.write(response.content)
            return True
        else:
            st.error(f"Error generating speech: {response.text}")
            return False
            
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return False

def process_audio(audio_bytes):
    try:
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        # Initialize speech recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file and convert to text
        with sr.AudioFile(tmp_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
        # Clean up temporary file
        os.unlink(tmp_file_path)
        return text
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None

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
        
        # Audio recording using Streamlit's native audio recorder
        audio_bytes = st.audio_recorder(
            text="Click to record your message",
            recording_color="#e87373",
            neutral_color="#6aa36f"
        )
        
        # Text input as fallback
        text_input = st.text_input("Or type your message here:", key="text_input")
        
        # Process audio if recorded
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            text = process_audio(audio_bytes)
            
            if text:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": text})
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    response = st.session_state.agent.generate_response(
                        text,
                        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                    )
                    message_placeholder.write(response)
                    
                    # Generate and play text-to-speech response
                    if play_text_as_speech(response):
                        st.audio("temp_audio.wav")
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Check if conversation should end
                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
                    
                st.rerun()
        
        # Process text input if provided
        elif text_input:
            st.session_state.messages.append({"role": "user", "content": text_input})
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                response = st.session_state.agent.generate_response(
                    text_input,
                    [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                )
                message_placeholder.write(response)
                
                # Generate and play text-to-speech response
                if play_text_as_speech(response):
                    st.audio("temp_audio.wav")
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Check if conversation should end
            if not st.session_state.agent.conversation_active:
                time.sleep(2)
                st.session_state.conversation_started = False
                
            st.rerun()

if __name__ == "__main__":
    main()
