from flask import Flask, request, send_file, jsonify
from flask import render_template
from pymongo import MongoClient
import gridfs
import os
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from PIL import Image
import io
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
# MongoDB connection
client = MongoClient(os.getenv("MONGO_CLIENT"))  # Change to your MongoDB URI
mongo_db = client["file_converter"]
fs = gridfs.GridFS(mongo_db)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "jpg", "png", "svg"}
UPLOAD_FOLDER = "uploads/"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def index():
    return render_template("index.html")

# Helper function to check file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Upload and Convert PDF to Word
@app.route("/convert/pdf-to-word", methods=["POST"])
def pdf_to_word():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Convert PDF to Word
        docx_path = file_path.replace(".pdf", ".docx")
        cv = Converter(file_path)
        cv.convert(docx_path)
        cv.close()
        
        # Store in MongoDB (GridFS)
        with open(docx_path, "rb") as converted_file:
            file_id = fs.put(converted_file, filename=os.path.basename(docx_path))
        
        # Delete local files
        os.remove(file_path)
        os.remove(docx_path)
        
        # Store metadata in MongoDB
        mongo_db.files.insert_one({
            "filename": filename,
            "original_format": "pdf",
            "converted_format": "docx",
            "status": "converted",
            "file_id": file_id
        })
        
        return jsonify({"message": "File converted successfully", "download_id": str(file_id)})
    
    return jsonify({"error": "Invalid file type"}), 400

# Route: Download Converted File
@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    file = fs.get(file_id)
    return send_file(io.BytesIO(file.read()), download_name=file.filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
