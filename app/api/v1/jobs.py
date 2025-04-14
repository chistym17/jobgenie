import feedparser
import requests
import json
import re
from datetime import datetime
from dateutil import parser
import hashlib
import html
import os

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    return ' '.join(text.strip().split())

def normalize_date(date_str: str) -> str:
    try:
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        parsed_date = parser.parse(date_str, ignoretz=True)
        return parsed_date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def generate_id(url: str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def is_engineering_job(title: str) -> bool:
    pattern = re.compile(r'\b(engineer(ing)?|software|sde|developer|dev)\b', re.IGNORECASE)
    return bool(pattern.search(title))

def parse_wwr_title(title: str) -> tuple:
    company = 'Unknown'
    job_title = clean_text(title)
    
    if ': ' in title:
        parts = title.split(': ', 1)
        company = clean_text(parts[0])
        job_title = clean_text(parts[1])
    elif ' at ' in title:
        parts = title.split(' at ', 1)
        job_title = clean_text(parts[0])
        company = clean_text(parts[1])
    
    company = re.sub(r'\s*\(?\s*hiring\s*\)?', '', company, flags=re.IGNORECASE).strip()
    
    return company, job_title

def fetch_wwr_jobs(existing_urls: set) -> list:
    jobs = []
    feed = feedparser.parse('https://weworkremotely.com/remote-jobs.rss')
    if not feed.entries:
        print("WWR feed empty or failed")
        return jobs
    for entry in feed.entries:
        company, title = parse_wwr_title(entry.title)
        job = {
            'id': generate_id(entry.link),
            'title': title,
            'company': company,
            'url': entry.link,
            'date': normalize_date(entry.get('published', '')),
            'source': 'We Work Remotely'
        }
        if is_engineering_job(job['title']) and job['url'] not in existing_urls:
            jobs.append(job)
            existing_urls.add(job['url'])
    return jobs

def fetch_remoteok_jobs(existing_urls: set) -> list:
    jobs = []
    try:
        response = requests.get('https://remoteok.com/api', timeout=10)
        response.raise_for_status()
        data = response.json()[1:]  
        for entry in data:
            job_date = normalize_date(entry.get('date', ''))
            if (datetime.now() - parser.parse(job_date)).days > 7:
                continue
            job = {
                'id': generate_id(entry['url']),
                'title': clean_text(entry.get('position', 'Untitled')),
                'company': clean_text(entry.get('company', 'Unknown')),
                'url': entry['url'],
                'date': job_date,
                'source': 'Remote OK'
            }
            if is_engineering_job(job['title']) and job['url'] not in existing_urls:
                jobs.append(job)
                existing_urls.add(job['url'])
    except requests.RequestException as e:
        print(f"Remote OK fetch failed: {e}")
    return jobs

def deduplicate_jobs(jobs: list) -> list:
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    return unique_jobs

def main():
    existing_urls = set()
    if os.path.exists('cleaned_jobs.json'):
        with open('cleaned_jobs.json', 'r', encoding='utf-8') as f:
            existing_jobs = json.load(f)
            existing_urls = {job['url'] for job in existing_jobs}
            print(f"Loaded {len(existing_jobs)} existing jobs for deduplication")

    wwr_jobs = fetch_wwr_jobs(existing_urls)
    remoteok_jobs = fetch_remoteok_jobs(existing_urls)

    all_jobs = wwr_jobs + remoteok_jobs

    unique_jobs = deduplicate_jobs(all_jobs)

    unique_jobs.sort(key=lambda x: x['date'], reverse=True)

    with open('all_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(unique_jobs, f, indent=2, ensure_ascii=False)

    print(f"\nTotal engineering jobs fetched: {len(unique_jobs)}")
    print(f" - WWR: {len(wwr_jobs)}")
    print(f" - Remote OK: {len(remoteok_jobs)}")
    print("\nSample (first 3 jobs or fewer):")
    for job in unique_jobs[:3]:
        print(json.dumps(job, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()