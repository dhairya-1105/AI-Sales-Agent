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
import threading

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
    if 'recording_started' not in st.session_state:
        st.session_state.recording_started = False
    if 'audio_recorder_key' not in st.session_state:
        st.session_state.audio_recorder_key = 0
    if 'first_recording' not in st.session_state:
        st.session_state.first_recording = True

def chunk_text(text, max_length=200):
    """Split text into chunks based on punctuation and length."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Split by sentences while preserving punctuation
    sentences = text.replace('!', '.').replace('?', '?|').replace('.', '.|').split('|')
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        sentence = sentence.strip()
        sentence_length = len(sentence)
        
        if current_length + sentence_length <= max_length:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def combine_wav_files(wav_contents):
    """Combine multiple WAV file contents into a single WAV file."""
    if not wav_contents:
        return None
        
    # Read the first WAV to get parameters
    with wave.open(io.BytesIO(wav_contents[0]), 'rb') as first_wav:
        params = first_wav.getparams()
        
    # Create output WAV in memory
    output_buffer = io.BytesIO()
    with wave.open(output_buffer, 'wb') as output_wav:
        output_wav.setparams(params)
        
        # Write all audio data
        for content in wav_contents:
            with wave.open(io.BytesIO(content), 'rb') as w:
                output_wav.writeframes(w.readframes(w.getnframes()))
    
    return output_buffer.getvalue()

def process_audio(audio_bytes):
    # Add small delay for first recording only
    if st.session_state.first_recording:
        time.sleep(1)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        temp_file.write(audio_bytes)
        temp_file.close()
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)
            
        text = recognizer.recognize_google(audio)
        st.session_state.first_recording = False
        return text
        
    except sr.UnknownValueError:
        st.session_state.first_recording = False
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        st.session_state.first_recording = False
        return "Sorry, there was an error with the speech recognition service."
    finally:
        os.unlink(temp_file.name)

def synthesize_and_play_speech(text, start_recording=True):
    """Synthesize speech and handle recording timing"""
    if not st.session_state.audio_response_played:
        text = ' '.join(text.replace('*', ' ').replace('−', '-').split())
        chunks = chunk_text(text, max_length=200)
        
        url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzdkNDZkNzcyZDk1YTBiMjZlMjI3ZWUiLCJ0eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM2MjYzMzgzLCJleHAiOjQ4OTIwMjMzODN9.vQSZlyYmkub1bBhjNghSD77Nt6HgVXK6hc62byFHbug",
            "Content-Type": "application/json"
        }
        
        try:
            # If starting recording, do it before synthesis
            if start_recording:
                st.session_state.recording_started = True
                st.session_state.audio_recorder_key += 1
                # Add extra delay for first recording
                if st.session_state.first_recording:
                    time.sleep(3)
                else:
                    time.sleep(2)
            
            wav_contents = []
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
            
            combined_audio = combine_wav_files(wav_contents)
            if combined_audio:
                st.audio(combined_audio, format='audio/wav', autoplay=True)
                st.session_state.audio_response_played = True
            
        except Exception as e:
            st.error(f"Error synthesizing speech: {str(e)}")

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    st.session_state.first_recording = True
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    synthesize_and_play_speech(welcome_message, start_recording=False)
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    st.session_state.audio_response_played = False

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
            if st.session_state.recording_started:
                audio_bytes = audio_recorder(
                    key=f"recorder_{st.session_state.audio_recorder_key}",
                    pause_threshold=3.0,
                    sample_rate=16000,
                    recording_color="#e74c3c",
                    neutral_color="#2ecc71",
                    icon_size="2x",
                    start_recording=True
                )
            else:
                audio_recorder(
                    key="inactive_recorder",
                    pause_threshold=3.0,
                    sample_rate=16000,
                    recording_color="#e74c3c",
                    neutral_color="#2ecc71",
                    icon_size="2x",
                    start_recording=False
                )

        if audio_bytes:
            st.session_state.audio_response_played = False
            st.session_state.recording_started = False
            
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
                    synthesize_and_play_speech(response, start_recording=True)

                st.session_state.messages.append({"role": "assistant", "content": response})

                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
            else:
                st.error(text)

if __name__ == "__main__":
    main()
