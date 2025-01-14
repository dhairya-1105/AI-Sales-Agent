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
import wave
import io

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
        word_length = len(word) + 1
        if current_length + word_length > max_length and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def combine_wav_files(wav_contents):
    """Combine multiple WAV file contents into a single WAV file."""
    if not wav_contents:
        return None
    
    # Use the first WAV file to get parameters
    with wave.open(io.BytesIO(wav_contents[0]), 'rb') as first_wav:
        params = first_wav.getparams()
    
    # Create output WAV in memory
    output = io.BytesIO()
    with wave.open(output, 'wb') as output_wav:
        output_wav.setparams(params)
        
        # Write all audio data
        for wav_content in wav_contents:
            with wave.open(io.BytesIO(wav_content), 'rb') as w:
                output_wav.writeframes(w.readframes(w.getnframes()))
    
    return output.getvalue()

def synthesize_speech(text):
    if not st.session_state.audio_response_played:
        text = ' '.join(text.replace('*', ' ').replace('−', '-').split())
        chunks = chunk_text(text, max_length=200)
        
        url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2Nzg1ZmNmNjQzNjMwNGZhZDUwODYwMjEiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM2ODM0Mjk0LCJleHAiOjQ4OTI1OTQyOTR9.iAA8qwiqaN8I1OJyJB0zN4sTlXZuowVqpIuu-Takfe4",
            "Content-Type": "application/json"
        }
        
        try:
            wav_contents = []
            
            # Get audio for all chunks
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
                    wav_contents.append(response.content)
                else:
                    st.error(f"Failed to synthesize chunk {i+1}: {response.text}")
                    return
            
            # Combine all WAV files
            combined_audio = combine_wav_files(wav_contents)
            if combined_audio:
                st.audio(combined_audio, format='audio/wav')
                st.session_state.audio_response_played = True
            
        except Exception as e:
            st.error(f"Error synthesizing speech: {str(e)}")

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    st.session_state.audio_response_played = False

def process_audio(audio_bytes):
    if audio_bytes is None:
        return None
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name
    
    try:
        r = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
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

    if not st.session_state.conversation_started:
        if st.button("Start Conversation"):
            start_conversation()

    if st.session_state.conversation_started:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        audio_container = st.container()
        
        with audio_container:
            st.write("Record your response below:")
            audio_bytes = audio_recorder(
                pause_threshold=2.0,
                sample_rate=16000
            )

        if audio_bytes:
            st.session_state.audio_response_played = False
            text = process_audio(audio_bytes)
            
            if text not in [None, "Sorry, I couldn't understand the audio.", "Sorry, there was an error with the speech recognition service."]:
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

                st.session_state.messages.append({"role": "assistant", "content": response})

                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
            else:
                st.error(text)

if __name__ == "__main__":
    main()
