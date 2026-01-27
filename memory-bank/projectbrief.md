# Brady Auto Label Date System

## Project Overview
The Brady Auto Label Date system is a specialized label generation and printing workstation. It automates the process of creating sequential labels with QR codes and date-based identifiers (Year/Month) for Brady-branded labeling solutions. The system ensures data integrity by preventing duplicate serial number usage through a backend tracking database.

## Core Requirements
- **System Selection**: Dropdown menu to choose the target system/product.
- **Auto-Date Detection**: Automatic selection of Year and Month based on the current system date.
- **Sequential Labeling**: Generate labels in batches based on a starting manual serial number.
- **Duplicate Prevention**: Real-time validation against a backend database to ensure serial numbers are not reused.
- **Label Formatting**:
    - High-density QR Code containing Year-Month-Serial.
    - Human-readable text at the bottom.
    - Specific styling: Arial font, size 8pt.
- **Backend Tracking**: SQL-based persistence to store history of generated labels and prevent duplicates.

## Key Goals
- Modernize the Brady label printing workflow with an automated, user-friendly interface.
- Guarantee 0% duplicate serial number generation.
- Reuse the robust ReportLab-based PDF generation architecture from the Nokia template.
- Implement a stable, focus-persistent frontend for high-throughput operational environments.

## Data Format
`[YEAR][MONTH][SERIAL]` (e.g., `2024010001` for January 2024, serial 0001)

