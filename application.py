from flask import Flask, request, jsonify, redirect
from SyllabusConverter import read_docx, query_chatgpt, setup_openai_api
import os
from dotenv import load_dotenv
from Calendar import get_google_calendar_service, create_events
import json 
import requests
from oauthlib.oauth2 import WebApplicationClient

application = Flask(__name__)

last_result = None

GOOGLE_CLIENT_ID = "166837721952-3qs3jse3grkcn5e9teggulm6fqavvba2.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@application.route('/')
def index():
    if last_result:
        return last_result
    else:
        return "No syllabus conversions have been done yet."

@application.route('/login')
def login():
    
    # Finds URL for Google login.
    
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['https://www.googleapis.com/auth/calendar.app.created'],
        prompt='consent'
    )
    return redirect(request_uri)

@application.route('/login/callback')
def callback():
    
    # Get authorization code from Google
    code = request.args.get('code')
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse tokens
    
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Finds URL from Google that contains user's profile information.
    
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get('email_verified'):
        unique_id = userinfo_response.json()['sub']
        users_email = userinfo_response.json()['email']
        picture = userinfo_response.json()['picture']
        users_name = userinfo_response.json()['name']

    # session['unique_id'] = unique_id
    # session['users_email'] = users_email
    # session['picture'] = picture
    # session['users_name'] = users_name
    
    return redirect("/")



@application.route('/upload', methods=['POST'])
def handle_upload():
    global last_result

    file = request.files['file']
    file_path = "files/" + file.filename
    file.save(file_path)

    # Assuming your script has a function like process_file(file_path)
    prompt = read_docx(file_path)

    result = query_chatgpt(prompt)

    # last_result = jsonify(result.content).get_data(as_text=True)
    last_result  = result.content

    credentials_path = 'credentials.json'
    service = get_google_calendar_service(credentials_path = credentials_path)

    new_calendar = {
        'summary': 'Quarter Schedule',
        'timeZone': 'America/Los_Angeles'
    }
    created_calendar = service.calendars().insert(body=new_calendar).execute()
    new_calendar_id = created_calendar['id']

    events_data = json.loads(last_result)
    create_events(service, new_calendar_id, events_data)
    return last_result


if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv('OPENAI_API_KEY')  # Get API key from environment variable
    print(api_key)
    setup_openai_api(api_key)
    application.run()

    