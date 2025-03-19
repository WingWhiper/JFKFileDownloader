import requests
from bs4 import BeautifulSoup
import os
import zipfile

def download_jfk_pdfs_and_zip():
    # URL of the JFK release page
    base_url = "https://www.archives.gov"
    page_url = "https://www.archives.gov/research/jfk/release-2025"

    # Make a GET request to fetch the page content
    response = requests.get(page_url)
    response.raise_for_status()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links that end with ".pdf"
    pdf_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.lower().endswith(".pdf"):
            pdf_links.append(href)

    # Create a folder to store downloaded PDFs
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    # Download each PDF link
    for pdf_link in pdf_links:
        # Build the absolute PDF URL if it's relative
        if pdf_link.startswith("http"):
            file_url = pdf_link
        else:
            # Join with base_url if needed
            file_url = base_url + pdf_link

        # Extract the file name from the link
        file_name = file_url.split("/")[-1]

        print(f"Downloading: {file_url}")
        # Download the PDF in chunks
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            pdf_path = os.path.join("pdfs", file_name)
            with open(pdf_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # Create a zip file containing all downloaded PDFs
    zip_filename = "jfk_release_2025_pdfs.zip"
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("pdfs"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "pdfs")
                zipf.write(file_path, arcname)

    print(f"All PDF files have been downloaded and zipped into {zip_filename}")

if __name__ == "__main__":
    download_jfk_pdfs_and_zip()
