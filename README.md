# Forecast

## 📘 Notebook Pipeline

A lightweight **FastAPI-based pipeline** that accepts an Excel file upload, executes a Jupyter notebook in an isolated job folder, and returns generated outputs such as `summary_report.pdf`.

---

## 🚀 What This Project Does

- 📤 Accepts an uploaded Excel file  
- 📁 Creates a unique job directory  
- 📝 Copies and runs a Jupyter notebook  
- 📄 Generates output files (PDF, executed notebook, etc.)  
- 📥 Allows you to download results via API endpoints  

---

## 📂 Project Structure

├── app.py
├── Minor.ipynb
├── requirements.txt
└── static/
└── upload.html

---

## ⚙️ Configuration (in `app.py`)

- `NOTEBOOK_PATH` → Notebook to execute (default: `Minor.ipynb`)  
- `EXPECTED_INPUT_FILENAME` → Input filename expected by the notebook (`sales.xlsx`)  
- `EXEC_TIMEOUT` → Timeout for notebook execution  

---

## 🧩 Prerequisites

- Python 3.10+  
- pip  
- (Optional) curl  

---

## 🪟 Installation — Windows (CMD)

### 1. Create a virtual environment
```cmd
python -m venv .venv
---

### 2. Activate it
```cmd
.venv\Scripts\activate
---

### 3. Install dependencies
```cmd
pip install -r requirements.txt
---

---

## 🐧 Installation — macOS / Linux (Bash)

### 1. Create a virtual environment
```bash
python3 -m venv .venv
---

### 2. Activate it
```bash
source .venv/bin/activate
---

### 3. Install dependencies
```bash
pip install -r requirements.txt
---

---

## ▶️ Running the App

Start the server:
```cmd
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
---

Open in browser:
```
http://localhost:8000/
```
---

## 🔌 API Usage

### 📤 Upload a File

**Bash**
curl -F "file=@data/sales.xlsx" http://localhost:8000/upload

markdown
Copy code

**Windows CMD**
curl -F "file=@data/sales.xlsx" http://localhost:8000/upload

yaml
Copy code

---

### 📊 Check Job Status

curl http://localhost:8000/status/<job_id>

makefile
Copy code

Example:
{
"exists": true,
"ready": false,
"produced_files": []
}

yaml
Copy code

---

### 📥 Download Output PDF

curl -o summary_report.pdf http://localhost:8000/download/<job_id>

yaml
Copy code

---

## 📄 Notebook Output Requirements

Your notebook must generate:

summary_report.pdf

yaml
Copy code

---

## 🛠 Troubleshooting

- PDF missing → Check `/status/<job_id>`  
- Notebook crashed → See `error.txt` in job folder  
- Long execution → Increase `EXEC_TIMEOUT`  

---
