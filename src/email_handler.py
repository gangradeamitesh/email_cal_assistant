import os
import base64
import ollama
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .logger import logger
#from my_config import MAX_EMAILS_TO_FETCH, EMAIL_SUMMARY_MAX_LENGTH, OLLAMA_MODEL
MAX_EMAILS_TO_FETCH = 10
EMAIL_SUMMARY_MAX_LENGTH = 200 
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"


class EmailHandler:
    """
    A class to handle Gmail operations including fetching, processing, and summarizing emails.
    
    This class provides functionality to:
    - Authenticate with Gmail API
    - Fetch today's emails
    - Filter promotional emails
    - Summarize email content using Ollama
    - Process and return email summaries
    
    Attributes:
        SCOPES (list): Gmail API scopes required for authentication
        creds (Credentials): Google API credentials
        service: Gmail API service instance
        promotional_indicators (list): Keywords used to identify promotional emails
    """

    def __init__(self):
        """
        Initialize EmailHandler with Gmail API authentication and promotional email indicators.
        """
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly' , 
                       "https://www.googleapis.com/auth/gmail.send"]
        self.creds = None
        self.service = None
        self.initialize_gmail()
        self.promotional_indicators = [
            'unsubscribe',
            'promotion',
            'special offer',
            'limited time',
            'discount',
            'sale',
            'newsletter',
            'marketing',
            'advertisement',
            'sponsored',
            'deal',
            'offer',
            'save',
            'exclusive',
            'subscribe'
        ]
    def is_promotional_email(self, email):
        """
        Check if an email is promotional based on its content and common patterns.

        Args:
            email (dict): Dictionary containing email data with 'subject' and 'body' keys

        Returns:
            bool: True if the email is promotional, False otherwise
        """
        # Convert email content to lowercase for case-insensitive matching
        content = f"{email['subject']} {email['body']}".lower()
        
        # Check for promotional indicators
        for indicator in self.promotional_indicators:
            if indicator in content:
                return True
                
        # Check for common promotional email patterns
        if 'unsubscribe' in content and ('http' in content or 'www' in content):
            return True
            
        return False

    def initialize_gmail(self):
        """
        Initialize Gmail API service and handle authentication.
        
        This method:
        1. Checks for existing credentials in token.json
        2. Refreshes expired credentials if possible
        3. Creates new credentials if none exist
        4. Builds the Gmail API service
        
        Raises:
            Exception: If authentication or service initialization fails
        """
        # Check if token.json exists
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If credentials are not valid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '', self.SCOPES) #provide your cred json
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_todays_emails(self):
        """
        Fetch today's emails, excluding promotional, social, and update categories.

        Returns:
            list: List of dictionaries containing email data (subject, sender, date, body)

        Raises:
            RuntimeError: If there's an error fetching emails
        """
        try:
            # Calculate today's date range
            today = datetime.now()
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Format date for Gmail API
            date_str = start_of_day.strftime("%Y/%m/%d")
            
            # Search for today's emails
            query = f'after:{date_str} -category:promotions -category:social -category:updates'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=MAX_EMAILS_TO_FETCH
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                # Get email details
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                date = next(h['value'] for h in headers if h['name'] == 'Date')

                # Get email body
                if 'parts' in msg['payload']:
                    body = self._get_email_body(msg['payload']['parts'])
                else:
                    body = base64.urlsafe_b64decode(
                        msg['payload']['body']['data']
                    ).decode('utf-8')

                email_data = {
                    'subject': subject,
                    'from': sender,
                    'received': date,
                    'body': body
                }
                #Commented to read all the emails
                # if not self.is_promotional_email(email_data):
                #     emails.append(email_data)
                emails.append(email_data)
            return emails

        except Exception as e:
            #logger.error(f"Error fetching emails: {str(e)}")
            raise RuntimeError(f"Error fetching emails: {str(e)}")

    def _get_email_body(self, parts):
        """
        Extract email body from message parts recursively.

        Args:
            parts (list): List of message parts from Gmail API

        Returns:
            str: Decoded email body text
        """
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body += base64.urlsafe_b64decode(
                    part['body']['data']
                ).decode('utf-8')
            elif 'parts' in part:
                body += self._get_email_body(part['parts'])
        return body

    def summarize_email(self, email_content):
        """
        Summarize email content using Ollama model.

        Args:
            email_content (str): The email content to summarize

        Returns:
            str: Summarized email content

        Raises:
            RuntimeError: If there's an error during summarization
        """
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": "You are an email summarization assistant. Provide concise summaries of emails."},
                    {"role": "user", "content": f"Summarize this email :\n\n{email_content}"}
                ]
            )
            return response['message']['content']
        except Exception as e:
            #logger.error(f"Error summarizing email: {str(e)}")
            raise RuntimeError(f"Error summarizing emails : {str(e)}")

    def process_todays_emails(self):
        """
        Process today's emails and return their summaries.

        This method:
        1. Fetches today's emails
        2. Summarizes each email
        3. Returns a list of email summaries with metadata

        Returns:
            list: List of dictionaries containing email summaries and metadata
                  Each dictionary contains: subject, from, received, and summary
        """
        emails = self.get_todays_emails()
        if not emails:
            return []
        

        # Summarize all emails
        email_summaries = []
        for email in emails:
            #logger.info(f"Processing email: {email['subject']} from {email['from']}")
            #logger.info(f"Email body : {email['body']}...")
            body = email['body']
            summary = self.summarize_email(
                f"Subject: {email['subject']}\n\nContent: {email['body']}"
            )
            email_summaries.append({
                'subject': email['subject'],
                'from': email['from'],
                'received': email['received'],
                'summary': summary
            })

        return email_summaries

    def get_emails_by_date_range(self, start_date: datetime, end_date: datetime):
        """
        Fetch emails within a specified date range.

        Args:
            start_date (datetime): Start date for email search
            end_date (datetime): End date for email search

        Returns:
            list: List of dictionaries containing email data (subject, sender, date, body)

        Raises:
            RuntimeError: If there's an error fetching emails
            ValueError: If start_date is after end_date
        """
        try:
            # Validate date range
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")

            # Format dates for Gmail API
            start_str = start_date.strftime("%Y/%m/%d")
            end_str = end_date.strftime("%Y/%m/%d")
            
            # Search for emails within date range
            query = f'after:{start_str} before:{end_str} -category:promotions -category:social -category:updates'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=MAX_EMAILS_TO_FETCH
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                # Get email details
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                date = next(h['value'] for h in headers if h['name'] == 'Date')

                # Get email body
                if 'parts' in msg['payload']:
                    body = self._get_email_body(msg['payload']['parts'])
                else:
                    body = base64.urlsafe_b64decode(
                        msg['payload']['body']['data']
                    ).decode('utf-8')

                email_data = {
                    'subject': subject,
                    'from': sender,
                    'received': date,
                    'body': body
                }
                emails.append(email_data)

            return emails

        except Exception as e:
            raise RuntimeError(f"Error fetching emails: {str(e)}")

    def process_emails_by_date_range(self, start_date: datetime, end_date: datetime):
        """
        Process emails within a date range and return their summaries.

        Args:
            start_date (datetime): Start date for email search
            end_date (datetime): End date for email search

        Returns:
            list: List of dictionaries containing email summaries and metadata
                  Each dictionary contains: subject, from, received, and summary
        """
        emails = self.get_emails_by_date_range(start_date, end_date)
        if not emails:
            return []

        # Summarize all emails
        email_summaries = []
        for email in emails:
            summary = self.summarize_email(
                f"Subject: {email['subject']}\n\nContent: {email['body']}"
            )
            email_summaries.append({
                'subject': email['subject'],
                'from': email['from'],
                'received': email['received'],
                'summary': summary
            })

        return email_summaries
    
    def send_email(self, to_email, subject, body, is_html=False):
        """
        Send an email.

        Args:
            to_email (str): Recipient's email address
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): Whether the body content is HTML

        Returns:
            dict: Response containing status and message
        """
        try:
            # Improve email body using Ollama
            improved_body = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an email writing assistant. Your task is to improve the given email content while maintaining its core message.
                        Guidelines:
                        1. Keep it professional and courteous
                        2. Maintain clear and concise language
                        3. Use proper grammar and punctuation
                        4. Structure the content logically
                        5. Keep the original intent and tone
                        6. Add appropriate greetings and closings if missing
                        7. Format paragraphs properly
                        8. Remove any inappropriate or unprofessional content"""
                    },
                    {
                        "role": "user",
                        "content": f"""Please improve this email while keeping its main message:
                        Subject: {subject}
                        Content: {body}"""
                    }
                ]
            )['message']['content']

            message = MIMEMultipart("alternative")
            message['to'] = to_email
            message['subject'] = subject
            logger.info(f"Improved Body : {improved_body}")
            if is_html:
                part = MIMEText(improved_body, 'html')
            else:
                part = MIMEText(improved_body, 'plain')
            message.attach(part)
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            sent_message = self.service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            return str({
                'status': 'success',
                'message_id': sent_message['id'],
                'message': "Email sent successfully",
                'improved_body': improved_body
            })
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "status": "Error",
                "message": f"Error sending email: {str(e)}"
            }
        
    


if __name__ == "__main__":
    email_handler = EmailHandler()
    today_summaries = email_handler.process_todays_emails()

    # Print today's email summaries
    for email in today_summaries:
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Time: {email['received']}")
        print(f"Summary: {email['summary']}")
        print("---")