import streamlit as st
import speech_recognition as sr
import requests
import tempfile
import time
from sales_agent import SalesAgent
import os
from audio_recorder_streamlit import audio_recorder
import base64

def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'waiting_for_audio' not in st.session_state:
        st.session_state.waiting_for_audio = False

def autoplay_audio(audio_content):
    b64 = base64.b64encode(audio_content).decode()
    md = f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    st.session_state.waiting_for_audio = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    play_text_as_speech(welcome_message)

def convert_audio_to_text(audio_bytes):
    r = sr.Recognizer()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio.flush()
        
        with sr.AudioFile(temp_audio.name) as source:
            audio_data = r.record(source)
            
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error with the speech recognition service."

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
            
            autoplay_audio(response.content)
            
            words = len(chunk.split())
            duration = (words / 2.5)
            time.sleep(duration)
            
        except Exception as e:
            print(f"Error processing chunk: {chunk}")
            print(f"Error: {str(e)}")
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
        
        # Create a placeholder for the audio recorder
        recorder_placeholder = st.empty()
        
        # Only show audio recorder when waiting for user input
        if st.session_state.waiting_for_audio:
            with recorder_placeholder:
                audio_bytes = audio_recorder(
                    text="Click to record your response",
                    recording_color="#e8b62c",
                    neutral_color="#6aa36f",
                    icon_name="user",
                    icon_size="6x",
                    pause_threshold=2.0,
                    sample_rate=41_000
                )
                
                if audio_bytes:
                    # Temporarily disable recorder while processing
                    st.session_state.waiting_for_audio = False
                    
                    # Convert audio to text
                    text = convert_audio_to_text(audio_bytes)
                    
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
                            st.session_state.waiting_for_audio = False
                            st.rerun()
                        else:
                            # Re-enable recorder for next response
                            st.session_state.waiting_for_audio = True
                            st.rerun()
                    else:
                        st.error(text)
                        # Re-enable recorder after error
                        st.session_state.waiting_for_audio = True
                        st.rerun()

if __name__ == "__main__":
    main()
