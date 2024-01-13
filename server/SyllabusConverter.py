import openai
from docx import Document
import os

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def setup_openai_api(api_key):
    openai.api_key = api_key

def query_chatgpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the GPT-4 model
            messages=[
                {
                    "role": "system", 
                    "content": "Scan the text for deadlines and grading related tasks. Extract and list the task name followed by its due date in this format: {'Summary': 'event name', 'start': {'dateTime': 'time'}, 'end':{'dateTime': 'time'} }. Event name is the name of the task, and time needs to be in a format like 2004-01-01T10:00:00 (by default from 23:30 to 23:59). If a recurring deadline like 'most Wednesdays' is mentioned, calculate and list all the specific Wednesdays' dates. The quarter starts on 09/23/2023 and ends on 12/09/2024 Use your best judgment for any ambiguous dates. Ensure that the list is sorted by start time. Only include the task name and its due date in the output."
                }, 
                {
                    "role": "user", 
                    "content": prompt
                }
                    ]
        )
        return response.choices[0].message
    except Exception as e:
        return str(e)
