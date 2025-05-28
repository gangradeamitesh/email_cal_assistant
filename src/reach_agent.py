from typing import List, Dict, Any 
from .email_handler import EmailHandler
from .calendar_handler import CalendarHandler
from .logger import logger
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import convert_to_messages
import json


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")
class ReActAssistant:
    def __init__(self) -> None:
        self.email_handler = EmailHandler()
        self.calender_handler = CalendarHandler()
        #self.tools = [self.email_handler.get_todays_emails , self.email_handler.summarize_email , self.calender_handler.create_event , self.calender_handler.get_upcoming_events]
        self.tools = [self.email_handler.send_email , self.email_handler.process_todays_emails , self.calender_handler.create_event , self.calender_handler.get_upcoming_events]
        
        self.llm  = ChatOllama(
            model="qwen3:0.6b",
            temperature=0,
             base_url="http://localhost:11434"
        )
        self.prompt =  f"""You are an AI assistant specialized in managing emails and calendar events. 
            You have access to the following tools:
                - process_todays_emails: Fetch and summarize today's emails
                - create_event: Create calendar events
                - get_upcoming_events: Get upcoming calendar events
                - send_email: Send emails to specified recipients

                Instructions:
                1. Always be clear and concise in your responses
                2. When handling emails:
                    - For reading emails:
                        • Provide a brief summary of each email
                        • List key points or action items
                        • Highlight any urgent or important information
                        • Include sender's email
                    - For sending emails:
                        • Confirm recipient's email address
                        • Verify email subject and content
                        • Format the email professionally
                        • Provide a confirmation of sending
                3. For calendar events:
                    - Confirm all details (time, date, location, attendees)
                    - Check for conflicts before creating
                    - Provide a confirmation summary
                4. If you're unsure about something, ask for clarification
                5. Format your responses in a user-friendly way:
                    - Use bullet points for lists
                    - Use clear section headers
                    - Highlight important information

                Example of a good email summary:
                📧 Email Summary
                From: sender@example.com
                Subject: Project Update
                Key Points:
                • Project milestone achieved
                • Next meeting scheduled
                • Action items for team

                Example of a good email sending response:
                📧 Email Sent Successfully
                To: recipient@example.com
                Subject: Project Update
                Status: Sent
                Message ID: [ID]

                Example of a good calendar response:
                📅 Calendar Event Created
                Event: Team Meeting
                Date: [Date]
                Time: [Time]
                Location: [Location]
                Attendees: [List]
                Confirmation: Event created successfully

                Please process this request and provide a helpful response."""
        self.agent = create_react_agent(
            tools = self.tools,
            model = self.llm,
            prompt=self.prompt
        )
    
    def process_request(self, user_input:str):
        """
        Process a user request and return the agent's response.

        Args:
            user_input (str): The user's input message

        Returns:
            str: The agent's response or error message if an exception occurs
        """
        logger.info(f"User Input to the agent: {user_input}")
        try:
            response_chunks = []
            execution_history = []
            for chunk in self.agent.stream(
                {"messages": [{"role": "user", "content": user_input}]}):
                #pretty_print_messages(chunk)
                # Store the response instead of just printing
                if isinstance(chunk, dict) and "agent" in chunk:
                    messages = chunk["agent"]['messages']
                    for m in messages:
                        if hasattr(m, "content"):
                            response_chunks.append(m.content)
                # if "tool_calls" in chunk['agent']:
                #     for tool_call in chunk['agent']['tool_calls']:
                #         execution_history.append({
                #             'tool':tool_call.get('name' , "unknown"),
                #             'arguments':tool_call.get('arguments' , {}),
                #             "result" : tool_call.get('resul',None)
                #         })
            if execution_history:
                logger.info("Tool Execution History :")
                for entry in execution_history:
                    logger.info(json.dumps(entry , indent = 2))
            full_response = " ".join(response_chunks)
            return full_response.strip()
        
        except Exception as e:
            import traceback
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.error(f"Error in ReAct agent: {error_details}")
            return f"Error processing request: {error_details['error_type']}: {error_details['error_message']}\n\nFull traceback:\n{error_details['traceback']}"
        

if __name__== "__main__":
    query = "Can you fetch my today's emails?"
    react = ReActAssistant()
    res = react.process_request(query)
    print(res)