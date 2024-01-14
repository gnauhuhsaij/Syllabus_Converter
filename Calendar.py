from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import json
import os
import requests

def get_google_calendar_service(server_base_url = "https://s2c-9ea6877338c9.herokuapp.com", credentials_path='credentials.json'):
    # Start the flow with the client secrets file
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        ['https://www.googleapis.com/auth/calendar']
    )
    
    # Generate an authorization URL with 'urn:ietf:wg:oauth:2.0:oob' as the redirect URI
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')

    # Send the URL to the user's local computer via your server's mechanism
    # For example, this could be an email, a message in your application, etc.
    requests.post(f"{server_base_url}/send_auth_link", data={'auth_url': auth_url})

    # Wait for the user to authorize and send back the authorization code
    # This is a simplified example; you'll likely want a more robust mechanism for this
    response = requests.get(f"{server_base_url}/retrieve_auth_code")
    auth_code = response.text

    # Finish the flow using the authorization code
    flow.fetch_token(code=auth_code)

    return googleapiclient.discovery.build('calendar', 'v3', credentials=flow.credentials)

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