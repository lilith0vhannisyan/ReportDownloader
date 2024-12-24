# Report Downloader

This project is a Streamlit-based web application for downloading student report files from a Moodle platform. Users can log in, specify a target URL, and download all collected student files as a ZIP file.

## Features
- Login to Moodle with your username and password.
- Specify the target URL of the quiz report page.
- Download student files (e.g., PDFs, .tex files) into a ZIP file.
- Handle students with the same names by creating unique folders.
- Mark students who didn't upload any files.

---

## Requirements
To run this project, ensure the following are installed on your system:

1. **Python 3.8 or higher**
2. The required Python libraries:
   - `requests`
   - `beautifulsoup4`
   - `streamlit`
   - `datetime`

---

## How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/lilith0vhannisyan/ReportDownloader.git
cd ReportDownloader
```

### 2. Install Dependencies
Manually install the required libraries using `pip`:

```bash
pip install requests
pip install beautifulsoup4
pip install streamlit
```

### 3. Run the Application
Run the application using Streamlit:

```bash
streamlit run download.py
```

### 4. Using the Application
1. Open the link provided in the terminal (usually `http://localhost:8501`).
2. Enter your Moodle username and password.
3. Paste the target URL for the Moodle quiz report page.
4. Click `Prepare Files` to process all student data.
5. Once processing is complete, click `Download All Files as ZIP` to download the ZIP file.

---

## Notes
- The application uses a single session to manage login and subsequent requests.
- Missing files or students who didn't upload any files will be highlighted in the application.
- Unique folders are created for students with the same names.

---

## Troubleshooting
### Common Issues
- **ModuleNotFoundError:** If you encounter an error about missing libraries, ensure all required libraries are installed.
- **Login Failed:** Double-check your Moodle credentials and the target URL.

### Debugging
Log messages are saved in a `download.log` file in the project directory for troubleshooting.

---

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
