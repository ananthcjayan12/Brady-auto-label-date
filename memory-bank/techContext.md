# Technical Context

## Tech Stack
- **Frontend:** React 18 (Vite), Tailwind CSS (for modern UI), Lucide Icons.
- **Backend:** Python 3.x, Flask.
- **Database:** SQLite (for tracking serial numbers).
- **PDF Generation:** ReportLab, `qrcode` (Python library).
- **OS Integration:** Native print commands (`lpr` for Unix, `powershell` for Windows).

## Development Setup
- **Backend Port:** `5001`
- **Frontend Port:** Managed by Vite (typically `5173`).
- **Required Python Packages:**
  - `flask`
  - `flask-cors`
  - `reportlab`
  - `qrcode`
  - `pypiwin32` (Windows only)

## Technical Constraints
- **Sequential Logic**: The system must handle increments accurately (e.g., `0001` to `0002`) while preserving leading zeros.
- **Database Consistency**: All label generation must be wrapped in a database transaction to ensure no serial number is skip-allocated or double-allocated.
- **UI Responsiveness**: Large batch generations (e.g., 500+ labels) should show a progress indicator or generate a single combined PDF for efficiency.

## Dependencies
- **ReportLab**: Primary tool for drawing QR codes and Arial 8pt text on PDF canvases.
- **qrcode**: Generates the matrix data for ReportLab to render.
- **Native OS Commands**:
  - `powershell` on Windows for `Start-Process -Verb PrintTo`.
  - `lpr` on Linux/Mac.

## Tool Usage Patterns
- **Backend Services**: `BradyLabelService` for logic, `DatabaseService` for persistence, `PrintService` for IO.
- **Frontend Components**: `LabelDashboard` for main control, `PreviewModal` for visual confirmation.

