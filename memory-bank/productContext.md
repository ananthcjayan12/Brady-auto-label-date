# Product Context

## Why this project exists?
In labeling and production environments, maintaining a sequential record of labels produced is critical for tracking and quality control. The Brady Auto Label Date system simplifies the creation of these labels by automating the date selection and ensuring that no two labels share the same serial number within a given time frame.

## Problems it solves
- **Duplicate Serial Numbers**: Manual tracking of serial numbers is prone to error, leading to duplicate labels on products. The system's backend database acts as a single source of truth.
- **Manual Data Entry Errors**: Automatically calculating the Year and Month reduces the need for user input and minimizes the risk of incorrect date formatting.
- **Batch Processing Efficiency**: Instead of generating labels one by one, users can generate a whole series (e.g., 100 labels) sequentially with a single click.
- **Inconsistent Formatting**: Ensures every label adheres to the exact specifications (QR code density, font size, layout).

## How it should work
1. **The User selects** a System and enters a starting serial number and the desired quantity.
2. **The Frontend** automatically identifies the current Year and Month. It then requests a batch of labels from the backend.
3. **The Backend** checks the SQLite database to ensure the requested serial range is available. If any serial number in the range has already been printed, it returns an error.
4. **The PDF Engine** (ReportLab) generates a combined PDF containing all requested labels. Each label feature:
    - A QR code containing the string `[YEAR][MONTH][SERIAL]`.
    - Human-readable text in **Arial 8pt** below the QR.
5. **The System** provides a print preview and sends the labels to the designated Brady printer.

## User Experience Goals
- **Error-Proof Workflow**: Prevent the printing process if a duplicate serial number is detected.
- **High Automation**: Minimize required clicks. Date and Month are pre-filled.
- **Visual Confidence**: Show a preview of the labels before they are sent to the printer.
- **Clean UI**: A focused, modern interface using the existing "Scan-to-Print" design philosophy.

