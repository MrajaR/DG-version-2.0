from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS


from LLMRAG import DangerousGoodsAnalyzer
from LLMRAG import Config

import os
import uuid

app = Flask(__name__)
CORS(app)

# Set a secret key to sign the session cookie
app.secret_key = Config.FLASK_SECRET_KEY  # Replace with a strong secret key

# PDF_FOLDER = 'user_pdf'
os.makedirs(Config.PDF_FOLDER, exist_ok=True)
analyzer = DangerousGoodsAnalyzer()

# Automatically assign a UUID to each new visitor
@app.before_request
def assign_user_uuid():
    """
    Automatically assigns a UUID to each new visitor. This is a before-request
    handler that checks if a user_id is already in the session. If not, it
    generates a new UUID and stores it in the session. This allows the same
    UUID to be used across multiple requests from the same user.
    """
    if 'user_id' not in session:
        # Generate and assign a new UUID for this session
        session['user_id'] = str(uuid.uuid4())
        print(f"Assigned new UUID: {session['user_id']}")

@app.route('/')
def index():
    # Get the UUID of the current user from the session
    """
    Displays the main page of the web application, which allows users to upload a PDF
    file and have it analyzed by the LLMRAG model.

    :return: The rendered HTML template for the main page
    """
    user_uuid = session.get('user_id')
    print(f"Current user UUID: {user_uuid}")
    
    return render_template('index.html')

@app.route('/analyze-msds', methods=['POST'])
def analyze_msds():
    """
    Endpoint to analyze a Material Safety Data Sheet (MSDS) document and return the
    relevant results in HTML format.

    :return: A JSON response containing the HTML content of the analysis
    """
    relevant_text = analyzer.get_relevant_chunks()
    print(relevant_text)
    llm_response = analyzer.get_llm_response(relevant_text)

    analyzer.delete_documents()

    print('response telah muncul dan dokumen telah di hapus')

    return jsonify({'Response': llm_response})

@app.route('/process-msds', methods=['POST'])
def process_uploaded_msds():
    """
    Handles the uploading and processing of a Material Safety Data Sheet (MSDS) PDF file.

    This endpoint expects a PDF file to be uploaded as part of a multipart/form-data request. The file is saved
    to a user-specific directory and processed using the DangerousGoodsAnalyzer. The user is identified by a
    unique session-based UUID.

    Returns:
        Response: A JSON response indicating the success or failure of the file upload and processing.
                  If the PDF file is not included in the request, an error response is returned.
    """
    user_id = session['user_id']

    if 'pdf' not in request.files:
        print('No file part in the request')
        return jsonify({'Response': 'Tolong upload file PDF'}), 400

    file = request.files['pdf']

    # Store file in a user-specific directory
    file_path = os.path.join(Config.PDF_FOLDER, file.filename)
    
    if file.filename in os.listdir(Config.PDF_FOLDER):
        print('File already exists in', Config.PDF_FOLDER)
        os.remove(file_path)

    file.save(file_path)
    print('File saved to', file_path)

    # Pass the user_id to the analyzer
    analyzer.process_document(file_path, user_id)

    return jsonify({'Response': 'MSDS processing success'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
