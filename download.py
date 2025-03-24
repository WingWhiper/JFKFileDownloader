#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import os
import zipfile
import gc
import psutil
from datetime import datetime

def get_memory_usage():
    """Returns the current memory usage in MB."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Memory in MB

def get_website_pdf_count():
    """Get the number of PDFs available on the website."""
    base_url = "https://www.archives.gov"
    page_url = "https://www.archives.gov/research/jfk/release-2025"
    
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    pdf_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.lower().endswith(".pdf"):
            pdf_links.append(href)
    
    return len(pdf_links), pdf_links

def get_local_pdf_count():
    """Get the number of PDFs in the local pdfs directory."""
    if not os.path.exists("pdfs"):
        return 0
    return len([f for f in os.listdir("pdfs") if f.lower().endswith('.pdf')])

def download_pdfs(pdf_links, base_url):
    """Download PDFs from the provided links."""
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    for pdf_link in pdf_links:
        if pdf_link.startswith("http"):
            file_url = pdf_link
        else:
            file_url = base_url + pdf_link

        file_name = file_url.split("/")[-1]
        pdf_path = os.path.join("pdfs", file_name)
        
        if os.path.exists(pdf_path):
            print(f"File already exists: {pdf_path}")
            continue

        print(f"Downloading: {file_url}")
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(pdf_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"Memory usage before garbage collection: {get_memory_usage():.2f} MB")
        del r
        del f
        gc.collect()
        print(f"Memory usage after garbage collection: {get_memory_usage():.2f} MB")

def create_zip_file():
    """Create a zip file of all PDFs in the pdfs directory with date in filename."""
    # Get current date in the format MM_DD_YYYY
    current_date = datetime.now().strftime("%m_%d_%Y")
    zip_filename = f"jfk_release_2025_pdfs_{current_date}.zip"
    print(f"Creating zip File: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("pdfs"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "pdfs")
                zipf.write(file_path, arcname)
    
    print(f"All PDF files have been zipped into {zip_filename}")

def main():
    # Get counts of PDFs
    website_count, pdf_links = get_website_pdf_count()
    local_count = get_local_pdf_count()
    
    print("\n=== JFK Files Downloader ===")
    print(f"PDFs available on website: {website_count}")
    print(f"PDFs in local directory: {local_count}")
    
    if website_count == local_count:
        print("\nYou have all the available PDFs downloaded.")
        response = input("Would you like to download them again? (yes/no): ").lower()
        if response != 'yes':
            print("Exiting program.")
            return
    
    elif website_count < local_count:
        print("\nWARNING: The number of PDFs on the website is less than what you have locally.")
        print("This could indicate that some documents have been removed from the website.")
        print("We recommend keeping your current files in a safe location and backed up for archival purposes.")
        response = input("Would you like to proceed with downloading? (yes/no): ").lower()
        if response != 'yes':
            print("Exiting program.")
            return
    
    else:  # website_count > local_count
        print(f"\nThere are {website_count - local_count} new PDFs available.")
        response = input("Would you like to download the new files? (yes/no): ").lower()
        if response != 'yes':
            print("Exiting program.")
            return
    
    # Download PDFs
    base_url = "https://www.archives.gov"
    download_pdfs(pdf_links, base_url)
    
    # Ask about creating zip file
    response = input("\nWould you like to create a zip file of all PDFs? (yes/no): ").lower()
    if response == 'yes':
        create_zip_file()
    
    print("\nDownload process completed!")

if __name__ == "__main__":
    main()
