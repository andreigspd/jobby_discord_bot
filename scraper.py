from bs4 import BeautifulSoup
import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# List of keywords commonly associated with IT / Tech positions
IT_KEYWORDS = [
    "developer", "engineer", "software", "programmer", "coder", "it", "tech",
    "data", "frontend", "front-end", "backend", "back-end", "fullstack", "full-stack",
    "web", "python", "java", "javascript", "typescript", "c++", "c#", ".net", "php",
    "ruby", "golang", "rust", "devops", "cloud", "sysadmin", "system", "network",
    "qa", "tester", "testing", "quality assurance", "scrum", "agile", "database",
    "dba", "cyber", "security", "ai", "ml", "machine learning", "deep learning",
    "android", "ios", "mobile", "react", "vue", "angular", "node", "ui", "ux",
    "product owner", "architect", "support engineer", "helpdesk", "infrastructure",
    "embedded", "bi", "analytics", "linus", "linux", "sql", "sap", "crm", "dev"
]

def is_it_job(title: str) -> bool:
    """Checks if a job title belongs to the IT/Tech domain."""
    if not title or title == "N/A":
        return False
    title_lower = title.lower()
    
    # Check if any IT keyword exists in the job title
    for kw in IT_KEYWORDS:
        # Match whole word or bounded substring (e.g., 'IT', 'Dev', 'Software')
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, title_lower):
            return True
            
    return False

def extract_job_id(link):
    """Extracts a unique numeric job ID from a LinkedIn URL."""
    if not link:
        return None
    clean = link.split("?")[0].rstrip("/")
    match = re.search(r'\b\d{9,11}\b', clean)
    if match:
        return match.group(0)
    parts = re.split(r'[-/]', clean)
    for part in reversed(parts):
        if part.strip().isdigit():
            return part.strip()
    return None

def scrape_linkedin_jobs(keywords, given_location, limit=10, enforce_it_only=True):
    """
    Scrapes LinkedIn's public guest job search API filtered specifically for IT jobs.
    Returns a list of job dictionaries.
    """
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    results = []
    
    # If the user keyword doesn't explicitly contain IT terms, append 'IT' to narrow down LinkedIn results
    query_keywords = keywords
    if enforce_it_only and not any(k in keywords.lower() for k in ["it", "software", "developer", "engineer", "tech", "programmer"]):
        query_keywords = f"{keywords} IT"

    # Scraping params including LinkedIn's IT Job Function filter ('f_F=it')
    params = {
        "keywords": query_keywords,
        "location": given_location,
        "f_F": "it",  # LinkedIn Guest Search Job Function filter for IT
        "start": 0
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"LinkedIn HTTP status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("li")
        
        for card in cards:
            if len(results) >= limit:
                break
                
            # Job Title
            title_elem = card.find("h3", class_="base-search-card__title")
            title = title_elem.text.strip() if title_elem else "N/A"
            
            # Filter out non-IT jobs if enforce_it_only is True
            if enforce_it_only and not is_it_job(title):
                continue
            
            # Company
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            company = company_elem.text.strip() if company_elem else "N/A"
            
            # Location
            location_elem = card.find("span", class_="job-search-card__location")
            location = location_elem.text.strip() if location_elem else "N/A"
            
            # Link
            link_elem = card.find("a", class_="base-card__full-link")
            link = link_elem["href"] if link_elem else None
            if not link:
                link_elem = card.find("a")
                link = link_elem["href"] if link_elem and "href" in link_elem.attrs else None
            if link:
                link = link.split("?")[0]
                
            job_id = extract_job_id(link)
            
            # Post date
            time_elem = card.find("time")
            post_date = "N/A"
            if time_elem:
                if "datetime" in time_elem.attrs:
                    post_date = time_elem["datetime"]
                else:
                    post_date = time_elem.text.strip()
                    
            if title != "N/A" or company != "N/A":
                results.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "post_date": post_date,
                    "link": link
                })
                
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
        return []
        
    return results

if __name__ == "__main__":
    print("Testing IT Filter with query 'Junior' in 'Romania':")
    jobs = scrape_linkedin_jobs("Junior", "Romania", limit=5)
    print(f"Found {len(jobs)} IT jobs:")
    for j in jobs:
        safe_str = str(j).encode('ascii', errors='replace').decode('ascii')
        print(safe_str)