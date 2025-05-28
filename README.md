# Personal Assistant

A simple AI assistant that helps you manage emails and calendar events using natural language.

## Demo

https://github.com/yourusername/Assist_Me/assets/your-user-id/demo-video.mp4

## Features

- 📧 Email Management
  - Read today's emails
  - Send emails
  - Get email summaries
  - Search emails by date

- 📅 Calendar Management
  - Create events
  - View upcoming events
  - Get event details

## Setup

1. Install Python 3.9 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the following APIs:
     - Gmail API
     - Google Calendar API
   - Create OAuth 2.0 credentials:
     - Click on "Credentials" in the left sidebar
     - Click "Create Credentials" and select "OAuth client ID"
     - Choose "Desktop application" as the application type
     - Give it a name (e.g., "Personal Assistant")
     - Click "Create"
   - Download the credentials:
     - After creating, you'll see a download button (JSON)
     - Click to download the credentials file
   - Place the credentials:
     - Rename the downloaded file to `credentials.json`
     - Place it in the root directory of this project
     - The file structure should look like:
       ```
       email_cal_assistant/
       ├── credentials.json    # Place your Google API credentials here
       ├── main.py
       ├── requirements.txt
       └── ...
       ```

4. Configure environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your credentials
   nano .env
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Example commands:
   - "Show my today's emails"
   - "Send an email to john@example.com about the meeting"
   - "Create a meeting tomorrow at 2 PM"
   - "Show my upcoming events"

## Configuration

You can modify these settings in your `.env` file:
- `OLLAMA_MODEL`: AI model to use (default: "gemma3:1b")
- `MAX_EMAILS_TO_FETCH`: Number of emails to fetch (default: 10)
- `EMAIL_SUMMARY_MAX_LENGTH`: Length of email summaries (default: 200)

## Security Note

- Never commit `.env` file or `credentials.json` to version control
- Keep your environment variables and API credentials secure and private
- Use `.env.example` as a template for required variables
- Regularly rotate your API credentials
- If you accidentally commit sensitive files, immediately revoke and regenerate your credentials

## Requirements

- Python 3.9+
- Google API credentials
- Ollama running locally
- Internet connection

## License

MIT License 