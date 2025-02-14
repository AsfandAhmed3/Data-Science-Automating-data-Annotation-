import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
import time
from urllib.parse import urljoin
import re
import json
import csv
from google.colab import files
import shutil
import threading
import glob

BASE_URL = "https://papers.nips.cc"
DATASETS_BENCHMARKS_URL_2021 = "https://datasets-benchmarks-proceedings.neurips.cc"
OUTPUT_DIR = "/content/research_papers_scraped/"
METADATA_DIR = "/content/metadata/"
THREAD_COUNT = 50
MAX_RETRIES = 3
TIMEOUT = 60
START_YEAR = 1987
END_YEAR = 2023

json_lock = threading.Lock()
csv_lock = threading.Lock()

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def download_pdf(session, pdf_url, filename):
    filename = sanitize_filename(filename)
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.pdf")
    if os.path.exists(filepath):
        print(f"File exists: {filepath}")
        return
    try:
        with session.get(pdf_url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded: {filepath}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")

def save_metadata_incremental_json(metadata, year):
    json_file = f"neurips_{year}.json"
    with json_lock:
        with open(json_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metadata, indent=4) + "\n")

def save_metadata_incremental_csv(metadata, year):
    csv_file = f"neurips_{year}.csv"
    headers = ["year", "title", "authors", "abstract", "pdf_url", "paper_url"]
    row = [
        metadata.get("year", ""),
        metadata.get("title", ""),
        "; ".join(metadata.get("authors", [])),
        metadata.get("abstract", ""),
        metadata.get("pdf_url", ""),
        metadata.get("paper_url", "")
    ]
    with csv_lock:
        write_header = not os.path.exists(csv_file)
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(headers)
            writer.writerow(row)

def process_paper_2022_2023(session, paper_url, year):
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(paper_url, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.text.strip().replace(" - NeurIPS", "") if soup.title else "Untitled"
            authors_h4 = soup.find('h4', string=re.compile("Authors", re.I))
            authors = []
            if authors_h4:
                authors_p = authors_h4.find_next('p')
                if authors_p:
                    authors = [a.strip() for a in authors_p.get_text(separator=",").split(",") if a.strip()]
            abstract_h4 = soup.find('h4', string=re.compile("Abstract", re.I))
            abstract = "No abstract available"
            if abstract_h4:
                abstract_p = abstract_h4.find_next('p')
                if abstract_p:
                    abstract = abstract_p.get_text(strip=True)
            pdf_link = soup.find('a', href=lambda href: href and href.endswith('Paper-Conference.pdf'))
            if not pdf_link:
                print(f"No PDF link found: {paper_url}")
                return
            pdf_url = urljoin(BASE_URL, pdf_link['href'])
            download_pdf(session, pdf_url, f"{year}_{title}")
            metadata = {
                "year": year,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "pdf_url": pdf_url,
                "paper_url": paper_url
            }
            year_dir = os.path.join(METADATA_DIR, str(year))
            os.makedirs(year_dir, exist_ok=True)
            metadata_filename = sanitize_filename(f"{title}") + ".json"
            metadata_filepath = os.path.join(year_dir, metadata_filename)
            with open(metadata_filepath, 'w') as f:
                json.dump(metadata, f, indent=4)
            save_metadata_incremental_json(metadata, year)
            save_metadata_incremental_csv(metadata, year)
            return
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {paper_url}: {e}")
            time.sleep(2 ** attempt)
    print(f"Giving up: {paper_url}")

def process_paper(session, paper_url, year):
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(paper_url, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('h4')
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"
            pdf_link = soup.find('a', href=lambda href: href and "Paper.pdf" in href)
            if not pdf_link:
                print(f"No PDF link: {paper_url}")
                return
            pdf_url = urljoin(BASE_URL, pdf_link['href'])
            authors_h4 = soup.find('h4', string=re.compile("Authors", re.I))
            authors = []
            if authors_h4:
                authors_p = authors_h4.find_next('p')
                if authors_p:
                    authors_text = authors_p.get_text(strip=True)
                    authors = [a.strip() for a in authors_text.split(",") if a.strip()]
            abstract_h4 = soup.find('h4', string=re.compile("Abstract", re.I))
            abstract = "No abstract available"
            if abstract_h4:
                abstract_p = abstract_h4.find_next('p')
                if abstract_p and not abstract_p.get_text(strip=True):
                    abstract_p = abstract_p.find_next('p')
                if abstract_p:
                    abstract = abstract_p.get_text(strip=True)
            download_pdf(session, pdf_url, f"{year}_{title}")
            metadata = {
                "year": year,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "pdf_url": pdf_url,
                "paper_url": paper_url
            }
            year_dir = os.path.join(METADATA_DIR, str(year))
            os.makedirs(year_dir, exist_ok=True)
            metadata_filename = sanitize_filename(f"{title}") + ".json"
            metadata_filepath = os.path.join(year_dir, metadata_filename)
            with open(metadata_filepath, 'w') as f:
                json.dump(metadata, f, indent=4)
            save_metadata_incremental_json(metadata, year)
            save_metadata_incremental_csv(metadata, year)
            return
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {paper_url}: {e}")
            time.sleep(2 ** attempt)
    print(f"Giving up: {paper_url}")

def process_dataset_benchmark_papers(session, url):
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paper_links = soup.select('a[href$="Abstract.html"]')
        for paper_link in paper_links:
            paper_url = urljoin(url, paper_link['href'])
            process_paper(session, paper_url, 2021)
    except Exception as e:
        print(f"Error processing datasets and benchmarks papers: {e}")

def get_user_years():
    while True:
        try:
            user_input = input(f"Enter up to 5 years (comma-separated) between {START_YEAR} and {END_YEAR}: ")
            years = [int(year.strip()) for year in user_input.split(",")]
            if len(years) > 5:
                print("Error: You can only select up to 5 years at a time.")
                continue
            invalid_years = [year for year in years if year < START_YEAR or year > END_YEAR]
            if invalid_years:
                print(f"Error: The following years are out of range: {invalid_years}")
                continue
            return years
        except ValueError:
            print("Error: Please enter valid years (e.g., 1987,1990,2023).")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)
    years_to_scrape = get_user_years()
    print(f"Scraping years: {years_to_scrape}")
    with requests.Session() as session:
        response = session.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        year_links = soup.select('a[href^="/paper_files/paper/"]')
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            for year_link in year_links:
                year_url = urljoin(BASE_URL, year_link['href'])
                try:
                    year = int(year_url.split('/')[-1])
                except (ValueError, IndexError):
                    print(f"Skipping invalid year URL: {year_url}")
                    continue
                if year in years_to_scrape:
                    print(f"Processing year: {year}")
                    try:
                        year_response = session.get(year_url)
                        year_soup = BeautifulSoup(year_response.text, 'html.parser')
                        if year > 2021:
                            paper_links = year_soup.select('a[href$="Abstract-Conference.html"]')
                        else:
                            paper_links = year_soup.select('a[href$="Abstract.html"]')
                        for paper_link in paper_links:
                            paper_url = urljoin(year_url, paper_link['href'])
                            if year > 2021:
                                executor.submit(process_paper_2022_2023, session, paper_url, year)
                            else:
                                executor.submit(process_paper, session, paper_url, year)
                    except Exception as e:
                        print(f"Year {year_url} error: {e}")
                else:
                    print(f"Skipping year {year} (not selected)")
            if 2021 in years_to_scrape:
                executor.submit(process_dataset_benchmark_papers, session, DATASETS_BENCHMARKS_URL_2021)

if __name__ == "__main__":
    main()
    choice = input("Do you want to download the scraped data as a ZIP file to your local PC? (Enter 'L' for local download or 'C' for Colab cloud storage): ").strip().lower()
    if choice == 'l':
        FINAL_OUTPUT_DIR = "/content/final_output"
        os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
        for f in glob.glob("/content/neurips_*.*"):
            if f.endswith(('.csv', '.json')):
                shutil.copy(f, FINAL_OUTPUT_DIR)
        shutil.copytree(METADATA_DIR, os.path.join(FINAL_OUTPUT_DIR, "metadata"))
        shutil.copytree(OUTPUT_DIR, os.path.join(FINAL_OUTPUT_DIR, "research_papers_scraped"))
        zip_filename = "/content/neurips_data.zip"
        shutil.make_archive("/content/neurips_data", 'zip', FINAL_OUTPUT_DIR)
        print(f"ZIP archive created: {zip_filename}. Downloading now...")
        files.download(zip_filename)
        shutil.rmtree(FINAL_OUTPUT_DIR)
    else:
        print("Files remain in the Colab cloud. You can access them in the workspace.")
