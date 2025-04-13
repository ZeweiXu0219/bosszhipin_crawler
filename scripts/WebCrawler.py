
import time
import logging
import random
from typing import List, Any, Optional

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    ElementClickInterceptedException
)

# For automatic webdriver management
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebCrawler:
    """Base web crawler class using Selenium."""
    
    def __init__(
        self, 
        headless: bool = True, 
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: int = 10,
        retry_count: int = 3,
        sleep_between_requests: tuple = (1, 3)
    ):
        """
        Initialize the web crawler.
        
        Args:
            headless: Whether to run the browser in headless mode
            user_agent: Custom user agent string
            proxy: Proxy server address (e.g., "http://proxy.example.com:8080")
            timeout: Default timeout for waiting operations (seconds)
            retry_count: Number of times to retry failed operations
            sleep_between_requests: Range of seconds to sleep between requests (min, max)
        """
        self.timeout = timeout
        self.mid_timeout = 3 * timeout
        self.long_timeout = 6 * timeout
        self.retry_count = retry_count
        self.sleep_between_requests = sleep_between_requests
        
        # Set up Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        
        # Add user agent if provided
        if user_agent:
            self.chrome_options.add_argument(f"user-agent={user_agent}")
        else:
            # Default user agent that looks like a regular browser
            self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Add proxy if provided
        if proxy:
            self.chrome_options.add_argument(f"--proxy-server={proxy}")
        
        # Additional options to make headless Chrome more stable
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the driver
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        """Initialize or reinitialize the WebDriver."""
        if self.driver:
            self.driver.quit()
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.driver.set_page_load_timeout(self.timeout)
        logger.info("WebDriver initialized")
    
    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to the specified URL with retry logic.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Navigating to {url} (Attempt {attempt + 1}/{self.retry_count})")
                self.driver.get(url)
                self._random_sleep()
                return True
            except Exception as e:
                logger.error(f"Error navigating to {url}: {str(e)}")
                if attempt < self.retry_count - 1:
                    self._random_sleep(multiplier=2)  # Longer sleep on failure
                else:
                    logger.error(f"Failed to navigate to {url} after {self.retry_count} attempts")
                    return False
    
    def find_element(
        self, 
        by: By, 
        value: str, 
        wait_time: Optional[int] = None,
        parent_element: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Find an element with wait and retry logic.
        
        Args:
            by: The locator strategy (e.g., By.ID, By.XPATH)
            value: The locator value
            wait_time: How long to wait for the element (defaults to self.timeout)
            parent_element: Parent element to search within (defaults to driver)
            
        Returns:
            The found element or None if not found
        """
        wait_time = wait_time or self.timeout
        if parent_element:
            search_context = parent_element
        else:
            search_context = self.driver
        
        try:
            element = WebDriverWait(search_context, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Element not found: {by}={value}, Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding element {by}={value}: {str(e)}")
            return None
    
    def find_elements(
        self, 
        by: By, 
        value: str, 
        wait_time: Optional[int] = None,
        parent_element: Optional[Any] = None
    ) -> List[Any]:
        """
        Find multiple elements with wait and retry logic.
        
        Args:
            by: The locator strategy (e.g., By.ID, By.XPATH)
            value: The locator value
            wait_time: How long to wait for the elements (defaults to self.timeout)
            parent_element: Parent element to search within (defaults to driver)
            
        Returns:
            List of found elements (empty list if none found)
        """
        wait_time = wait_time or self.timeout
        if parent_element:
            search_context = parent_element
        else:
            search_context = self.driver
        
        try:
            WebDriverWait(search_context, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return search_context.find_elements(by, value)
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"No elements found: {by}={value}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error finding elements {by}={value}: {str(e)}")
            return []
    
    def click_element(self, element, retry_count: Optional[int] = None) -> bool:
        """
        Click an element with retry logic.
        
        Args:
            element: The element to click
            retry_count: Number of retries (defaults to self.retry_count)
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        retry_count = retry_count or self.retry_count
        
        for attempt in range(retry_count):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self._random_sleep(0.5, 1)
                
                # Try to click
                element.click()
                self._random_sleep()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                logger.warning(f"Click failed (Attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    self._random_sleep(multiplier=1.5)
                else:
                    logger.error(f"Failed to click element after {retry_count} attempts")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error clicking element: {str(e)}")
                return False
    
    def extract_text(self, element) -> str:
        """
        Safely extract text from an element.
        
        Args:
            element: The element to extract text from
            
        Returns:
            str: The extracted text or empty string if failed
        """
        try:
            return element.text.strip()
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_attribute(self, element, attribute: str) -> str:
        """
        Safely extract an attribute from an element.
        
        Args:
            element: The element to extract the attribute from
            attribute: The name of the attribute to extract
            
        Returns:
            str: The attribute value or empty string if failed
        """
        try:
            value = element.get_attribute(attribute)
            return value if value else ""
        except Exception as e:
            logger.error(f"Error extracting attribute {attribute}: {str(e)}")
            return ""
    
    def wait_for_page_load(self, timeout: Optional[int] = None):
        """
        Wait for the page to finish loading.
        
        Args:
            timeout: How long to wait (defaults to self.timeout)
        """
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("Timed out waiting for page to load")
    
    def _random_sleep(self, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None, multiplier: float = 1.0):
        """
        Sleep for a random amount of time within the specified range.
        
        Args:
            min_seconds: Minimum sleep time (defaults to self.sleep_between_requests[0])
            max_seconds: Maximum sleep time (defaults to self.sleep_between_requests[1])
            multiplier: Multiply the sleep range by this value
        """
        min_time = (min_seconds if min_seconds is not None else self.sleep_between_requests[0]) * multiplier
        max_time = (max_seconds if max_seconds is not None else self.sleep_between_requests[1]) * multiplier
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
