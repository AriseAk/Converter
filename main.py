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
from bson.objectid import ObjectId
from docx import Document
from fpdf import FPDF

app = Flask(__name__)

load_dotenv()
# MongoDB connection
client = MongoClient(os.getenv("MONGO_CLIENT"))  # Change to your MongoDB URI
mongo_db = client["file_converter"]
fs = gridfs.GridFS(mongo_db)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "jpg", "png", "svg" ,"jpeg" ,"docx"}
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
        return "<p style='color:red;'>No file uploaded!</p>", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "<p style='color:red;'>No selected file!</p>", 400
    
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

        # Return HTML response for HTMX
        return f"<p style='color:green;'>File converted! <a href='/download/{file_id}'>Download Word File</a></p>"
    
    return "<p style='color:red;'>Invalid file type!</p>", 400

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Converted PDF", ln=True, align="C")

@app.route("/convert/word-to-pdf", methods=["POST"])
def word_to_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith(".docx"):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Convert DOCX to PDF
        pdf_path = file_path.replace(".docx", ".pdf")
        doc = Document(file_path)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for para in doc.paragraphs:
            text = para.text
            text = text.encode("latin-1", "ignore").decode("latin-1")  # Fix encoding issue
            pdf.multi_cell(0, 10, txt=text, align="L")

        pdf.output(pdf_path)

        # Store in MongoDB (GridFS)
        with open(pdf_path, "rb") as converted_file:
            file_id = fs.put(converted_file, filename=os.path.basename(pdf_path))

        # Delete local files
        os.remove(file_path)
        os.remove(pdf_path)

        # Store metadata in MongoDB
        mongo_db.files.insert_one({
            "filename": filename,
            "original_format": "docx",
            "converted_format": "pdf",
            "status": "converted",
            "file_id": file_id
        })

        return f"<p style='color:green;'>File converted! <a href='/download/{file_id}'>Download PDF File</a></p>"

    return "<p style='color:red;'>Invalid file type!</p>", 400


@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))  # Convert file_id to ObjectId
        return send_file(io.BytesIO(file.read()), 
                         download_name=file.filename, 
                         as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found or invalid ID"}), 404


# Route: Display Converted Files
@app.route("/converted-files", methods=["GET"])
def converted_files():
    files = list(mongo_db.files.find({}, {"filename": 1, "file_id": 1}))
    return render_template("converted.html", files=files)

if __name__ == "__main__":
    app.run(debug=True)
