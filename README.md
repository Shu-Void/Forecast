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
```

### 2. Activate it
```cmd
.venv\Scripts\activate
```

### 3. Install dependencies
```cmd
pip install -r requirements.txt
```

## 🐧 Installation — macOS / Linux (Bash)

### 1. Create a virtual environment
```bash
python -m venv .venv
```

### 2. Activate it
```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## ▶️ Running the App

Start the server:
```cmd
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open in browser:
```
http://localhost:127.0.0.1:8000/
(http://127.0.0.1:8000 )
```

## 📄 Notebook Output Requirements

Your notebook must generate:
```
summary_report.pdf
```

## 🛠 Troubleshooting

- PDF missing → Check `/status/<job_id>`  
- Notebook crashed → See `error.txt` in job folder  
- Long execution → Increase `EXEC_TIMEOUT`
