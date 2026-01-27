# Scan-to-Print Workstation Template

A modular template for building automated scan-to-print workstations using a **React Frontend** and a **Python/Flask Local Print Bridge**.

## Architecture

This project follows a split-architecture model designed for reliability in industrial/warehouse environments:

1.  **Frontend (React/Vite):** Handles logic for scanner input handling, barcode parsing, and real-time label previewing.
2.  **Print Server (Python/Flask):** A local service that runs on the workstation. It receives PDF generation requests and immediately sends them to the connected label printer via native OS commands (`lpr` on Linux/macOS, `SumatraPDF` or `print` on Windows).

## Project Structure

- `frontend/`: React source code.
- `print-server/`: Python backend for PDF generation and printing.
- `memory-bank/`: Documentation system for AI-assisted development.
- `.github/workflows/`: Automated CI/CD for Cloudflare Pages.

## Getting Started

### 1. Setup the Local Print Server
```bash
cd print-server
pip install -r requirements.txt
python app.py
```

### 2. Setup the Frontend
```bash
cd frontend
npm install
npm run dev
```

## How to Customize

1.  **Barcode Logic:** Modify `frontend/src/App.jsx` to change how the raw scan string is parsed.
2.  **Label Layout:** Modify `print-server/services.py` to change the PDF generation (ReportLab) dimensions and design.
3.  **Deployment:** Update `.github/workflows/deploy.yml` with your Cloudflare project details.

---
Created from [ananthcjayan12/Brady-auto-scan-pdf](https://github.com/ananthcjayan12/Brady-auto-scan-pdf).
