from flask import Flask, render_template, request, flash, redirect, url_for
import os
import easyocr
import logging
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this!

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize OCR reader once (not per request)
reader = easyocr.Reader(['en'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    start_time = time.time()
    
    if 'image' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('home'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('home'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed. Please upload an image.')
        return redirect(url_for('home'))
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        result = reader.readtext(filepath, detail=0, paragraph=True)
        
        # Clean up
        os.remove(filepath)
        
        text = "\n".join(result) if result else "No text detected"
        
        processing_time = round(time.time() - start_time, 2)
        logging.info(f"Processed {filename} in {processing_time}s")
        
        return render_template("result.html", text=text, processing_time=processing_time)
    
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        flash('Error processing image. Please try again.')
        return redirect(url_for('home'))

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)