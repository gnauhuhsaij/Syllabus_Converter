from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import json
import os

def get_google_calendar_service(credentials_path='credentials.json'):
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        ['https://www.googleapis.com/auth/calendar']
    )
    creds = flow.run_local_server(port=8080)
    return googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

def create_events(service, calendar_id, events_data):
    for event_data in events_data:
        event = {
            'summary': event_data['summary'],
            'start': {'dateTime': event_data['start'], 'timeZone': 'America/Los_Angeles'},
            'end': {'dateTime': event_data['end'], 'timeZone': 'America/Los_Angeles'}
        }

        try:
            # Make API request and handle errors
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event created: {event['htmlLink']}")
        except Exception as e:
            print(f"Error creating event: {e}")

# def main():
#     credentials_path = 'credentials.json'
#     service = get_google_calendar_service(credentials_path)

#     calendar_id = 'primary'

#     with open('syllabus_events.json', 'r') as file:
#         events_data = json.load(file)

#     # Call the function to create events
#     create_events(service, calendar_id, events_data)