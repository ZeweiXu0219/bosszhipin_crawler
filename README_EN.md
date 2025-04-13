# Zhipin Job Crawler

A web crawler designed to scrape job listings from [zhipin.com](https://www.zhipin.com/) (BOSS直聘), a popular Chinese job listing platform.

## Features

- Search for jobs with specific criteria (job title, location, etc.)
- Filter results by job type, experience, salary, education, company size, and financing stage
- Navigate through multiple pages of search results
- Extract detailed job information including:
  - Job title
  - Company information (name, industry, financing stage, size)
  - Location
  - Salary range
  - Experience requirements
  - Education requirements
  - Contact information
- Handles login popups automatically
- Implements retry logic for robust web scraping
- Mimics human-like browsing behavior with random delays

## Requirements

- Python 3.6+
- Chrome browser
- Dependencies listed in `requirements.txt`:
  - selenium
  - webdriver-manager
  - tqdm

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ZeweiXu0219/bosszhipin_crawler.git
   cd zhipin_crawler
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Make sure you have Chrome browser installed on your system.

## Usage

### Basic Usage

```python
from scripts.JobListingCrawler import JobListingCrawler

# Initialize the crawler
crawler = JobListingCrawler(headless=False)  # Set to True for headless mode

# Search for jobs
job_listings = crawler.search_jobs(
    url="https://www.zhipin.com/web/geek/job?query=",
    query="NLP算法",  # Job title/keyword
    location="北京"   # Location
)

# Print found job listings
print(f"Found {len(job_listings)} job listings.")

# Navigate through multiple pages
for i in range(4):
    crawler.click_page()  # Go to next page
    new_jobs = crawler.scan_page()
    print(f"Found {len(new_jobs)} more job listings on page {i+2}.")

# Always close the crawler when done
crawler.close()
```

### Advanced Filtering

The crawler supports advanced filtering using the `select_menu.json` configuration:

```python
# Define filter options
options = {
    "求职类型": ["全职"],           # Job type: Full-time
    "工作经验": ["3-5年"],          # Experience: 3-5 years
    "薪资待遇": ["20-50K"],         # Salary: 20-50K
    "学历要求": ["本科"],           # Education: Bachelor's degree
    "公司规模": ["10000人以上"],    # Company size: 10000+ employees
    "融资阶段": ["已上市"]          # Financing stage: Listed company
}

# Get URL with filters applied
filtered_url = crawler.get_full_select_url(base_url, "data/select_menu.json", options)
crawler.navigate_to_url(filtered_url)
```

## Project Structure

- `main.py`: Example script demonstrating usage of the crawler
- `requirements.txt`: List of required Python packages
- `scripts/`:
  - `WebCrawler.py`: Base crawler class with common web scraping functionality
  - `JobListingCrawler.py`: Specialized crawler for job listings
  - `PopupMonitor.py`: Utility for handling login popups
- `data/`:
  - `select_menu.json`: Configuration for filtering options

## Features in Detail

### WebCrawler Class

The base `WebCrawler` class provides:

- Browser initialization with configurable options (headless mode, user agent, proxy)
- Navigation with retry logic
- Element finding with wait and retry logic
- Safe element interaction (clicking, text extraction)
- Random delays to mimic human behavior

### JobListingCrawler Class

Extends the base crawler with job-specific functionality:

- Job search with location and keyword filtering
- Advanced filtering using select_menu.json configuration
- Extraction of job listings from search results
- Pagination through search results
- Controlled scrolling to load dynamic content

### PopupMonitor Class

Handles login popups that may appear during crawling:

- Multiple monitoring strategies (loop, WebDriverWait, MutationObserver)
- Automatic closing of login dialogs
- Resource cleanup

## Notes

- The crawler is designed to work with the zhipin.com website structure as of the time of development. Website changes may require updates to the selectors.
- Use responsibly and in accordance with the website's terms of service and robots.txt file.
- Consider adding delays between requests to avoid overloading the target website.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
