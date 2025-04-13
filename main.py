import logging
from tqdm import tqdm
from scripts.JobListingCrawler import JobListingCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Example usage of the JobListingCrawler."""
    try:
        # Initialize the crawler
        crawler = JobListingCrawler(headless=False)  # Set to True for headless mode
        # monitor = PopupMonitor(crawler.driver, crawler.driver.current_url)
        # monitor.monitor_popup_mutation_observer()         
        # Example: Search for jobs
        job_listings = crawler.search_jobs(
            url="https://www.zhipin.com/web/geek/job?query=",
            query="NLP算法",
            location="北京"
        )

        logging.info(f"Found {len(job_listings)} job listings in one page.")
        
        jobs = [job_listings]
        for i in tqdm(range(4)):
            crawler._random_sleep(2,4)
            crawler.click_page()
            new_jobs = crawler.scan_page()
            jobs.append(new_jobs)
        
        # # Example: Get details for each job
        # for i, job in enumerate(job_listings[:5]):  # Limit to first 5 for example
        #     print(f"\nJob {i+1}: {job['title']} at {job['company']}")
            
        #     if job['url']:
        #         details = crawler.get_job_details(job['url'])
        #         print(f"Description: {details.get('description', '')[:100]}...")  # First 100 chars
        #         print(f"Requirements: {', '.join(details.get('requirements', []))}")
            
        # Always close the crawler when done
        # monitor.stop_monitoring()
        crawler.close()
        return jobs
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        # Ensure the crawler is closed even if an error occurs
        if 'crawler' in locals():
            crawler.close()
    

if __name__ == "__main__":
    jobs = main()
    # By.CLASS_NAME

