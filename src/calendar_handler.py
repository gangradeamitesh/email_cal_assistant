import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .logger import logger
import json 
# from config import OLLAMA_MODEL
import ollama
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"
class CalendarHandler:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        self.service = None
        self.initialize_calendar()

    def initialize_calendar(self):
        """Initialize Google Calendar API service"""
        # Check if token.json exists
        if os.path.exists('calendar_token.json'):
            self.creds = Credentials.from_authorized_user_file('', self.SCOPES) #Provide you cred json
        
        # If credentials are not valid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '', self.SCOPES) #Provide you credenstion.json
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('calendar_token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, title, start_time, end_time, description="", location="", attendees=None):
        """Create a new calendar event"""
        try:
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # Indian Standard Time
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send email notifications to attendees
            ).execute()

            return {
                'status': 'success',
                'event_id': event['id'],
                'htmlLink': event['htmlLink']
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_upcoming_events(self, max_results=10):
        """Get upcoming calendar events"""
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events

        except Exception as e:
            print(f"Error fetching events: {str(e)}")
            return []

    def parse_event_details(self, user_input):
        """Parse event details from user input using Ollama"""
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a calendar event parser. Extract event details from user input.
                        Return a JSON with these fields:
                        - title: Event title
                        - start_time: Event start time (ISO format)
                        - end_time: Event end time (ISO format)
                        - description: Event description
                        - location: Event location
                        - attendees: List of attendee emails
                        If any field is not mentioned, return null for that field.
                        and do not write json keyword before the json object."""
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )
            
            # Parse the response and create event
            content = response['message']['content']
            # for i in range(len(content)):
            #     if content[i] == '{':
            #         content = content[i:]
            #         break
            # parsed_content = ""
            # for j in range(len(content)):
            #     if content[j] != "}":
            #         parsed_content += content[j]
            parsed_content = self.get_substring(content , "{" , "}")
            logger.info("Parsed content : " , parsed_content)
            event_details = json.loads(parsed_content)
            logger.info(f"Parsed event details: {event_details}")
            return event_details

        except Exception as e:
            logger.error(f"Error parsing event details: {str(e)}")
            raise RuntimeError(f"Error parsing event details: {str(e)}")

    def process_calendar_request(self, user_input):
        """Process calendar-related requests"""
        try:
            # Parse event details from user input
            event_details = self.parse_event_details(user_input)
            if not event_details:
                return "Could not understand the event details. Please try again with more specific information."

            # Create the event
            result = self.create_event(
                title=event_details.get('title'),
                start_time=datetime.datetime.fromisoformat(event_details.get('start_time')),
                end_time=datetime.datetime.fromisoformat(event_details.get('end_time')),
                description=event_details.get('description', ''),
                location=event_details.get('location', ''),
                attendees=event_details.get('attendees', [])
            )

            if result['status'] == 'success':
                return f"Event created successfully! You can view it here: {result['htmlLink']}"
            else:
                return f"Error creating event: {result['message']}"

        except Exception as e:
            return f"Error processing calendar request: {str(e)}"

    def get_substring(self, text , start_marker , end_marker):
        try:
            start = text.find(start_marker) 
            end = text.find(end_marker)
            if start == -1 or end == -1:
                return ""
            return text[start:end+1]
        except:
            return ""

if __name__ == "__main__":
    calendar_handler = CalendarHandler()
    
    # Example usage
    test_input = "Schedule a meeting with Himanshu (himanshutiwari.tiwari93@gmail.com) 25th May 2025 at 2 PM for 1 hour to discuss project updates"
    result = calendar_handler.process_calendar_request(test_input)
    print(result) 