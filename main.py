import streamlit as st
from src.chat_interface import ChatInterface
from src.reach_agent import ReActAssistant

def main():
    # Initialize and run the chat interface
    chat_interface = ChatInterface()
    chat_interface.run()

if __name__ == "__main__":
    main()