import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import requests
import tempfile
import os
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

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    synthesize_speech(welcome_message)

def synthesize_speech(text):
    # Clean the text
    text = ' '.join(text.replace('*', ' ').replace('−', '-').split())
    
    url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2Nzc5MDI4MGM0NDE1ODdhYjZlODEwM2UiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM1OTgzNzQ0LCJleHAiOjQ4OTE3NDM3NDR9._Rhof8jciBrL8FBN1rR8-qX8GJOlrKcg9fbMnJxRbXc",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "voice_id": "mithali",
        "add_wav_header": True,
        "sample_rate": 16000,
        "speed": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Display audio in Streamlit
            st.audio(response.content, format='audio/wav')
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
        
        # Audio recording using streamlit-audio-recorder
        audio_bytes = audio_recorder()
        
        if audio_bytes:
            text = process_audio(audio_bytes)
            
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
                    synthesize_speech(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Check if conversation should end
                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
            else:
                st.error(text)
            
            st.rerun()

if __name__ == "__main__":
    main()
