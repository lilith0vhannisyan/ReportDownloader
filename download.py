import os
import requests
from bs4 import BeautifulSoup
import zipfile
import streamlit as st
from datetime import datetime
import io

# Define constants
BASE_URL = "https://moodle.ufar.am"

# Create a session for login and subsequent requests
session = requests.Session()

# Define today's date for folder naming
today_date = datetime.now().strftime("%Y-%m-%d")

def login_to_moodle(username, password):
    """
    Logs in to Moodle using provided credentials.
    """
    try:
        login_page = session.get(f"{BASE_URL}/login/index.php")
        soup = BeautifulSoup(login_page.text, 'html.parser')

        # Extract the logintoken
        logintoken = soup.find('input', {'name': 'logintoken'}).get('value', '')

        login_payload = {
            'username': username,
            'password': password,
            'logintoken': logintoken
        }

        response = session.post(f"{BASE_URL}/login/index.php", data=login_payload)
        if response.ok and "login" not in response.url:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error during login: {e}")
        return False

def download_file(file_url):
    """Downloads a single file and returns its content."""
    try:
        file_response = session.get(file_url)
        if file_response.ok:
            return file_response.content
        else:
            return None
    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return None

def create_unique_folder_name(student_name, existing_names):
    """
    Creates a unique folder name by appending a number if necessary.
    """
    folder_name = student_name
    counter = 1
    while folder_name in existing_names:
        folder_name = f"{student_name}_{counter}"
        counter += 1
    return folder_name

def process_student(row, existing_names, missing_files_students):
    """Processes a single student's files."""
    try:
        # Extract student name
        name_element = row.select_one('td.c2 a')
        if not name_element:
            return None, []

        student_name = name_element.text.strip()
        folder_name = create_unique_folder_name(student_name, existing_names)
        existing_names.add(folder_name)

        # Extract link to detailed attempt page
        attempt_link = row.select_one('td.c8 a')['href']
        attempt_url = f"{BASE_URL}{attempt_link}" if attempt_link.startswith('/') else attempt_link

        # Access the detailed attempt page
        attempt_response = session.get(attempt_url)
        attempt_soup = BeautifulSoup(attempt_response.text, 'html.parser')

        # Locate the attachments section
        attachments_div = attempt_soup.find('div', class_='attachments')
        if not attachments_div:
            missing_files_students.append(f"{folder_name} - Empty (No files uploaded)")
            return folder_name, []

        # Extract file links
        file_links = attachments_div.find_all('a')
        file_data = []

        # Download each file
        for link in file_links:
            file_url = f"{BASE_URL}{link['href']}" if link['href'].startswith('/') else link['href']
            file_name = link.text.strip()
            file_content = download_file(file_url)
            if file_content:
                file_data.append((file_name, file_content))
            else:
                missing_files_students.append(f"{folder_name} - Failed to download {file_name}")

        return folder_name, file_data

    except Exception as e:
        st.error(f"Error processing row for {student_name}: {e}")
        missing_files_students.append(f"{folder_name} - Error")
        return None, []

def download_files(target_url):
    """
    Accesses all pages from the target URL, parses them for files, and prepares them for download.
    """
    try:
        page_number = 1
        current_page_url = target_url
        missing_files_students = []
        collected_files = {}
        existing_names = set()

        while current_page_url:
            response = session.get(current_page_url)
            if not response.ok:
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Process student rows on the current page
            rows = soup.select('tr[id^="mod-quiz-report-overview-report_r"]')

            for row in rows:
                folder_name, file_data = process_student(row, existing_names, missing_files_students)
                if folder_name is not None:
                    collected_files[folder_name] = file_data

            # Check for the next page link
            next_page = soup.select_one('nav.pagination a[aria-label="Next"]')
            if next_page and 'href' in next_page.attrs:
                current_page_url = next_page['href']
                current_page_url = f"{BASE_URL}{current_page_url}" if current_page_url.startswith('/') else current_page_url
                page_number += 1
            else:
                current_page_url = None  # No more pages to process

        # Create a ZIP file of all downloaded files, including empty folders
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for folder_name, files in collected_files.items():
                if not files:
                    zipf.writestr(f"{folder_name}/", "")
                for file_name, file_content in files:
                    zipf.writestr(f"{folder_name}/{file_name}", file_content)
        zip_buffer.seek(0)

        return zip_buffer, missing_files_students

    except Exception as e:
        st.error(f"Error during file download: {e}")
        return None, []

# Streamlit App
st.title("Moodle Downloader")
st.info("Provide your Moodle login credentials and the target URL to download all student files.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
target_url = st.text_input("Target URL")
download_button = st.button("Prepare Files")

if download_button:
    if login_to_moodle(username, password):
        zip_buffer, missing_files_students = download_files(target_url)
        if zip_buffer:
            st.download_button("Download All Files as ZIP", zip_buffer, file_name=f"collected_files_{today_date}.zip")
        if missing_files_students:
            st.warning("The following students had issues with their uploads:")
            for student in missing_files_students:
                st.write(student)
