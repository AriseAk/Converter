Here’s a well-structured **README.md** file along with a **requirements.txt** file for your repository:  

---

### **README.md**
```md
# File Converter Web App

This is a Flask-based file conversion web application that allows users to convert files between different formats. The converted files are stored in MongoDB using GridFS, and old files are automatically deleted after 7 days.

## 📌 Features
- ✅ Convert **PDF to Word (.docx)**
- ✅ Convert **Word (.docx) to PDF**
- ✅ Convert **JPG to SVG**
- ✅ Store converted files in MongoDB GridFS
- ✅ Automatically delete files after 7 days using APScheduler

---

## 🚀 Installation

### 📋 Prerequisites
- **Python 3.x** installed
- **MongoDB** (with GridFS enabled)
- **Render account** (for deployment)

### 🔧 Setup & Run Locally
1. **Clone the repository**  
   ```sh
   git clone <repo-url>
   cd <project-folder>
   ```

2. **Create a virtual environment** (optional but recommended)  
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**  
   Create a `.env` file in the project root and add:
   ```env
   MONGO_CLIENT=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
   ```

5. **Run the application**  
   ```sh
   python app.py
   ```

6. Open your browser and visit `http://127.0.0.1:5000`

---

## 🌍 Deployment on Render
1. **Create a new Web Service** on [Render](https://render.com/)
2. **Connect your GitHub repository**
3. **Set the build & run commands**  
   - **Build Command:**  
     ```sh
     pip install -r requirements.txt
     ```
   - **Start Command:**  
     ```sh
     gunicorn app:app
     ```
4. **Add environment variables in Render's dashboard**
5. **Deploy and access your app via the provided URL**

---

## 🛠 Technologies Used
- **Flask** - Backend framework
- **MongoDB (GridFS)** - File storage
- **APScheduler** - Automated file deletion
- **pdf2docx, FPDF, Pillow** - File conversions

---

## 🗑 Automatic File Deletion
- Converted files are stored in **MongoDB GridFS**.
- A background job runs every **hour** to check for expired files (older than **7 days**) and deletes them automatically.

---
