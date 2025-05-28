import streamlit as st
import ollama
from datetime import datetime
from .email_handler import EmailHandler
from .calendar_handler import CalendarHandler
from .logger import logger
from .reach_agent import ReActAssistant
import warnings
warnings.filterwarnings('ignore')
# from src.my_config import OLLAMA_MODEL

OLLAMA_MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"
# Initialize session state using setdefault

class ChatInterface:
    def __init__(self):
        self.email_handler = EmailHandler()
        self.calendar_handler = CalendarHandler()
        self.ollama_model = OLLAMA_MODEL
        self.react_agent = ReActAssistant()

    def process_user_input(self, user_input):
        """Process user input and determine intent"""
        try:
            st.write("Debug - User Input : " , user_input)
            # Use Ollama to determine if the request is for email or calendar
            response = self.react_agent.process_request(user_input)
            response = self.extract_response(response)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"
    def extract_response(self , response):
        try:
            if "</think>" in response:
                return response.split("</think>")[1].strip()
        except Exception:
            return response
                
    def run(self):
        """Run the Streamlit interface"""
        st.title("Personal Assistant")
        st.write("I can help you manage your emails and calendar events.")

        # Display chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("What would you like me to help you with?"):
            # Add user message to chat history
            st.session_state['messages'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get assistant response
            with st.chat_message("assistant"):
                response = self.process_user_input(prompt)
                st.markdown(response)
                st.session_state['messages'].append({"role": "assistant", "content": response})
        
# if __name__ == "__main__":
#     chat_interface = ChatInterface()
#     chat_interface.run() 