# Forecast

📘 Notebook Pipeline — README
🚀 What this project does

This is a FastAPI-based notebook execution pipeline.
Users upload an Excel file → the server copies a Jupyter notebook → executes it → generates outputs such as summary_report.pdf → returns it for download.

Core logic is inside app.py.

📁 Project structure

You should have:

app.py — FastAPI backend

Minor.ipynb — the notebook that gets executed

requirements.txt — Python dependencies

static/upload.html — simple web upload form (optional)

⚙️ Default configuration (in app.py)

NOTEBOOK_PATH = "Minor.ipynb"

EXPECTED_INPUT_FILENAME = "sales.xlsx"

EXEC_TIMEOUT = <number_of_seconds>

Make sure your notebook expects sales.xlsx, OR change the value in the code.

🧩 Prerequisites

Python 3.10+

pip

🟦 Installation (Windows CMD)
1. Create virtual environment
python -m venv .venv

2. Activate venv
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

🟩 Installation (macOS / Linux — Bash)
1. Create virtual environment
python3 -m venv .venv

2. Activate venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

▶️ Running the app
Windows CMD
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

macOS / Linux (Bash)
uvicorn app:app --host 0.0.0.0 --port 8000 --reload


Now open in browser:

http://localhost:8000/


Upload your Excel file → processing begins.

🧪 API Usage (Both Bash & Windows CMD)
📤 Upload a file
Bash
curl -F "file=@data/sales.xlsx" http://localhost:8000/upload

CMD (double quotes slightly different)
curl -F "file=@data/sales.xlsx" http://localhost:8000/upload

📊 Check job status
Bash
curl http://localhost:8000/status/<job_id>

CMD
curl http://localhost:8000/status/<job_id>

📥 Download PDF
Bash
curl -o summary_report.pdf http://localhost:8000/download/<job_id>

CMD
curl -o summary_report.pdf http://localhost:8000/download/<job_id>

📄 What the notebook must produce

Inside each job folder, the notebook should generate:

summary_report.pdf


You can change this filename in app.py if needed.

🛠 Troubleshooting
❗ No PDF found

Check /status/<job_id> → see produced files.

❗ Notebook failing

Look inside the job folder → error.txt contains traceback.

❗ Long notebooks

Increase EXEC_TIMEOUT in app.py.
