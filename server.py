from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from llm_rag import DangerousGoodsAnalyzer
import os
import uuid

app = Flask(__name__)
CORS(app)

# Set a secret key to sign the session cookie
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

UPLOAD_FOLDER = 'user_pdf'
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

@app.route('/save_n_examine_doc', methods=['POST'])
def save_and_examine():
    # Ensure the user has a UUID
    user_uuid = session.get('user_id')
    if not user_uuid:
        return jsonify({'error': 'User not identified'}), 400
    
    print(f"Processing request for user with UUID: {user_uuid}")

    if 'pdf' not in request.files:
        return jsonify({'error':'No File Found'}), 400
    
    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({'error' : 'No Selected File'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        print(f"Received file: {filename}")

        # Create a user-specific folder to save their files
        user_folder = os.path.join(UPLOAD_FOLDER, user_uuid)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Save the file to the user's folder
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        print(f"File saved to {file_path}")

        # Process the file with your DangerousGoodsAnalyzer
        is_process_ok = analyzer.ocr_pdf(file_path, user_uuid)
        print(f"PDF OCR processing result: {is_process_ok}")

        if is_process_ok == False:
            os.remove(file_path)
            return jsonify({'error': 'Maaf, saya hanya bisa memproses dokumen MSDS'}), 400
        
        return jsonify({'result' : 'MSDS berhasil diupload'})

    return jsonify({'error': 'Unexpected error occurred'}), 500


@app.route('/process-document', methods=['POST'])
def process_uploaded_doc():
    user_id = session.get('user_id')

    with open(f'MSDS_text/{user_id}.txt', 'r') as f:
        msds_text = f.read()

    result = analyzer.process_document(msds_text)
    print(result)
        
    return jsonify({'result': result})
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
