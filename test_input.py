import requests

# URL of your Flask server
url = 'https://s2c-9ea6877338c9.herokuapp.com/upload'

# Path to the file you want to upload
file_path = '../A.docx'

# Open the file in binary mode
with open(file_path, 'rb') as file:
    # Define the files dictionary. The key ('file' in this case) should match the key expected by your Flask server.
    files = {'file': file}
    
    # Send the POST request
    response = requests.post(url, files=files)

    # Print the response from the server
    if response.ok:
        print("Server Response:", response.json())
    else:
        print("Error occurred:", response.text)
