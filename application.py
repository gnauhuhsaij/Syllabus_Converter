from flask import Flask, request, jsonify
from SyllabusConverter import read_docx, query_chatgpt, setup_openai_api
import os
from dotenv import load_dotenv
from Calendar import get_google_calendar_service, create_events
import json 

application = Flask(__name__)

last_result = None

@application.route('/')
def index():
    if last_result:
        return last_result
    else:
        return "No syllabus conversions have been done yet."

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
    service = get_google_calendar_service(credentials_path)

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
    setup_openai_api(api_key)
    from waitress import serve
    serve(application, host="0.0.0.0", port=8080)

    