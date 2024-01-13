from flask import Flask, request, jsonify
from SyllabusConverter import read_docx, query_chatgpt, setup_openai_api
import os
from dotenv import load_dotenv

app = Flask(__name__)

last_result = None

@app.route('/')
def index():
    if last_result:
        return last_result
    else:
        return "No syllabus conversions have been done yet."

@app.route('/upload', methods=['POST'])
def handle_upload():
    global last_result

    file = request.files['file']
    file_path = "files/" + file.filename
    file.save(file_path)

    # Assuming your script has a function like process_file(file_path)
    prompt = read_docx(file_path)

    result = query_chatgpt(prompt)

    last_result = jsonify(result.content).get_data(as_text=True)
    # print(result)
    return last_result


if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv('OPENAI_API_KEY')  # Get API key from environment variable
    setup_openai_api(api_key)
    app.run(debug=True) 