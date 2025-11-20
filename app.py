# app.py
import os
import shutil
import uuid
import tempfile
import asyncio
import traceback
import nbformat

from pathlib import Path
from typing import Optional

from nbconvert.preprocessors import ExecutePreprocessor
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

# -------------------- CONFIG --------------------
NOTEBOOK_PATH = "Minor.ipynb"          # notebook located next to app.py
EXPECTED_INPUT_FILENAME = "sales.xlsx" # filename notebook expects (change only if notebook expects different name)
EXEC_TIMEOUT = 10 * 60                 # 10 minutes
# Use system temp dir to avoid Windows path issues (spaces etc)
JOBS_DIR = os.path.join(tempfile.gettempdir(), "notebook_jobs")
os.makedirs(JOBS_DIR, exist_ok=True)
# ------------------------------------------------

app = FastAPI(title="Notebook pipeline (robust)")

# Serve static upload page from ./static/upload.html
app.mount("/static", StaticFiles(directory="static"), name="static")


# -------------------- Helpers --------------------
async def run_notebook_in_dir(nb_path: str, work_dir: str):
    """
    Execute the notebook at nb_path with working directory work_dir.
    Raises exception on failure.
    """
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=EXEC_TIMEOUT, kernel_name="python3")
    old_cwd = os.getcwd()
    try:
        os.chdir(work_dir)
        ep.preprocess(nb, {"metadata": {"path": work_dir}})
    finally:
        os.chdir(old_cwd)

    # Save executed copy for inspection
    executed_path = os.path.join(work_dir, "executed.ipynb")
    try:
        with open(executed_path, "w", encoding="utf-8") as ef:
            nbformat.write(nb, ef)
    except Exception:
        # non-fatal if saving executed copy fails
        pass


def pdf_exists(work_dir: str) -> Optional[str]:
    """
    Return path to summary_report.pdf if it exists inside work_dir (root).
    """
    candidate = os.path.join(work_dir, "summary_report.pdf")
    if os.path.exists(candidate):
        return candidate
    return None


def collect_files(work_dir: str):
    """Return list of files in work_dir (rel paths) sorted by mtime desc."""
    files = []
    for p in Path(work_dir).rglob("*"):
        if p.is_file():
            try:
                files.append((str(p.relative_to(work_dir)), p.stat().st_mtime))
            except Exception:
                files.append((str(p.relative_to(work_dir)), 0))
    files.sort(key=lambda x: x[1], reverse=True)
    return [f for f, _ in files]


# -------------------- Routes --------------------
@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the static upload HTML page."""
    index_path = os.path.join("static", "upload.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<html><body><h3>Upload page not found. Put static/upload.html</h3></body></html>")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload: create job folder, save excel, copy notebook, start background job."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    job_id = str(uuid.uuid4())
    job_folder = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_folder, exist_ok=True)

    # Save uploaded file with the expected filename
    dest_path = os.path.join(job_folder, EXPECTED_INPUT_FILENAME)
    try:
        contents = await file.read()
        with open(dest_path, "wb") as out_f:
            out_f.write(contents)
    except Exception as e:
        # cleanup on failure
        shutil.rmtree(job_folder, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
    finally:
        try:
            file.file.close()
        except Exception:
            pass

    # Copy notebook into job folder (use the same name the run expects)
    try:
        shutil.copy2(NOTEBOOK_PATH, os.path.join(job_folder, os.path.basename(NOTEBOOK_PATH)))
    except Exception as e:
        # cleanup and fail
        shutil.rmtree(job_folder, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to copy notebook: {e}")

    # Start background job
    asyncio.create_task(_background_run_job(job_id))

    return {"ok": True, "job_id": job_id}


async def _background_run_job(job_id: str):
    job_folder = os.path.join(JOBS_DIR, job_id)
    nb_path = os.path.join(job_folder, os.path.basename(NOTEBOOK_PATH))
    try:
        await run_notebook_in_dir(nb_path, job_folder)
    except Exception as e:
        # record error for debugging
        tb = traceback.format_exc()
        try:
            with open(os.path.join(job_folder, "error.txt"), "w", encoding="utf-8") as ef:
                ef.write(tb)
        except Exception:
            pass


@app.get("/status/{job_id}")
def status(job_id: str):
    job_folder = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_folder):
        return {"exists": False}

    # error file present?
    err_file = os.path.join(job_folder, "error.txt")
    if os.path.exists(err_file):
        return {"exists": True, "ready": False, "error": True, "produced_files": collect_files(job_folder)}

    # pdf ready?
    pdf_path = pdf_exists(job_folder)
    if pdf_path:
        return {"exists": True, "ready": True, "produced_files": collect_files(job_folder)}

    return {"exists": True, "ready": False, "produced_files": collect_files(job_folder)}


@app.get("/download/{job_id}")
async def download_pdf(job_id: str):
    """
    Robust download:
     - reads the file into memory to avoid Windows file streaming/lock race conditions
     - writes download_error.txt in job folder with full traceback if read fails
     - schedules deletion of job folder after a delay
    """
    job_folder = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_folder):
        return JSONResponse(status_code=404, content={"ok": False, "error": "job not found"})

    pdf_path = pdf_exists(job_folder)
    if not pdf_path:
        return JSONResponse(status_code=404, content={"ok": False, "error": "PDF not ready or not found", "produced_files": collect_files(job_folder)})

    try:
        # read into memory
        with open(pdf_path, "rb") as pf:
            pdf_bytes = pf.read()
    except Exception as e:
        tb = traceback.format_exc()
        # write diagnostic file
        try:
            with open(os.path.join(job_folder, "download_error.txt"), "w", encoding="utf-8") as df:
                df.write(tb)
        except Exception:
            pass
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e), "traceback": tb})

    # schedule cleanup after giving time for client to receive
    asyncio.create_task(_delayed_cleanup(job_id, delay_seconds=12))

    # return as in-memory Response to avoid streaming/locking problems
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=summary_report.pdf"},
    )


async def _delayed_cleanup(job_id: str, delay_seconds: int = 10):
    await asyncio.sleep(delay_seconds)
    job_folder = os.path.join(JOBS_DIR, job_id)
    try:
        shutil.rmtree(job_folder, ignore_errors=True)
    except Exception:
        pass
