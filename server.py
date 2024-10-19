from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from LLMRAG import DangerousGoodsAnalyzer
import os
import uuid

app = Flask(__name__)
CORS(app)

# Set a secret key to sign the session cookie
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

PDF_FOLDER = 'user_pdf'
os.makedirs(PDF_FOLDER, exist_ok=True)
analyzer = DangerousGoodsAnalyzer()

# Automatically assign a UUID to each new visitor
@app.before_request
def assign_user_uuid():
    if 'user_id' not in session:
        # Generate and assign a new UUID for this session
        session['user_id'] = str(uuid.uuid4())
        print(f"Assigned new UUID: {session['user_id']}")

@app.route('/')
def index():
    # Get the UUID of the current user from the session
    user_uuid = session.get('user_id')
    print(f"Current user UUID: {user_uuid}")
    
    return render_template('index.html')

@app.route('/analyze-msds', methods=['POST'])
def analyze_msds():
    relevant_text = analyzer.get_relevant_chunks()
    print(relevant_text)
    llm_response = analyzer.get_llm_response(relevant_text)

    analyzer.delete_documents()

    print('response telah muncul dan dokumen telah di hapus')

    return jsonify({'Response': llm_response})

@app.route('/process-msds', methods=['POST'])
def process_uploaded_msds():
    user_id = session['user_id']

    if 'file' not in request.files:
        return jsonify({'Response': 'Tolong upload file PDF'}), 400

    file = request.files['file']

    # Store file in a user-specific directory
    file_path = os.path.join(PDF_FOLDER, file.filename)
    
    if file.filename in os.listdir(PDF_FOLDER):
        print('File already exists in', PDF_FOLDER)
        os.remove(file_path)

    file.save(file_path)
    print('File saved to', file_path)

    # Pass the user_id to the analyzer
    analyzer.process_document(file_path, user_id)

    return jsonify({'Response': 'MSDS processing success'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
