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
                # Add extra delay for the first recording
                if st.session_state.first_recording:
                    time.sleep(3)  # Longer initial delay
                else:
                    time.sleep(2)  # Regular delay for subsequent recordings
            
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

def process_audio(audio_bytes):
    # Add delay for first recording
    if st.session_state.first_recording:
        time.sleep(1)  # Add a small delay before processing first recording
    
    try:
        # Your existing audio processing code here
        # ...
        st.session_state.first_recording = False  # Mark first recording as completed
        return text
    except Exception as e:
        st.session_state.first_recording = False  # Mark as completed even if error occurs
        return "Sorry, I couldn't understand the audio."

def start_conversation():
    st.session_state.agent = SalesAgent(api_key="your-groq-api-key")
    st.session_state.conversation_started = True
    st.session_state.first_recording = True  # Reset first recording flag
    welcome_message = "Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested in exploring our mattress options?"
    # Don't start recording for the initial welcome message
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
                    # Start recording before playing the response
                    synthesize_and_play_speech(response, start_recording=True)

                st.session_state.messages.append({"role": "assistant", "content": response})

                if not st.session_state.agent.conversation_active:
                    time.sleep(2)
                    st.session_state.conversation_started = False
            else:
                st.error(text)

if __name__ == "__main__":
    main()
