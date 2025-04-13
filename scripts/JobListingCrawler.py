"""
Basic Selenium Web Crawler Framework

This script provides a basic framework for web crawling using Selenium.
Before running, make sure to install the required packages:
    pip install selenium webdriver-manager

The webdriver-manager package helps manage browser drivers automatically.
"""
import os
import time
import json
import random
import logging
from tqdm import tqdm
from functools import wraps
from scripts.WebCrawler import WebCrawler
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional, Callable, TypeVar

# Selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')

def with_retry(
    retries: int = 3,
    retry_delay: tuple[float, float] = (0.5, 1.5),
    specific_exceptions: tuple = (Exception,),
    on_retry_callback: Optional[Callable] = None
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    A decorator that implements retry logic for any function.
    
    Args:
        retries: Maximum number of retry attempts
        retry_delay: Tuple of (min_delay, max_delay) for random wait between retries
        specific_exceptions: Tuple of exception types to catch and retry on
        on_retry_callback: Optional callback function to execute between retries
        
    Returns:
        The decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            for attempt in range(retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except specific_exceptions as e:
                    logger.warning(f"{func.__name__} failed (Attempt {attempt + 1}/{retries}): {str(e)}")
                    
                    if attempt < retries - 1:
                        # Random sleep between retries
                        sleep_time = random.uniform(retry_delay[0], retry_delay[1])
                        if attempt > 0:  # Increase wait time for subsequent attempts
                            sleep_time *= (attempt + 1)
                            
                        logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        
                        # Execute callback if provided
                        if on_retry_callback:
                            on_retry_callback(*args, **kwargs)
                    else:
                        logger.error(f"Failed to execute {func.__name__} after {retries} attempts")
                        return None
            return None
        return wrapper
    return decorator


class JobListingCrawler(WebCrawler):
    """Example extension of WebCrawler for job listings."""
    
    def __init__(self, **kwargs):
        """Initialize the job listing crawler."""
        super().__init__(**kwargs)
        self.results = []
        self.login_phone = "13213222228"
        cur_path = os.getcwd()
        self.select_menu_path = os.path.join(cur_path, "data/select_menu.json")
    
    def search_city(self, desired_city: str) -> bool:
        all_listed_city = [
            "全国",
            "北京",
            "上海",
            "广州",
            "深圳",
            "杭州",
            "西安",
            "天津",
            "苏州",
            "武汉",
            "厦门",
            "成都",
            "长沙",
            "郑州",
            "重庆"
        ]
        if desired_city not in all_listed_city:
            return False
        try:
            city_area_dropdown = self.find_element(By.CSS_SELECTOR, ".city-area-dropdown")

            # 2. Click the "城市和区域" tab if it's not already active (most common case)
            city_tab = self.find_element(By.XPATH, ".//ul[@class='city-area-tab']/li[text()='城市和区域']")
            if "active" not in city_tab.get_attribute("class"):
                city_tab.click()

            # 3. Locate and click the desired city
            city_element = self.find_element(By.XPATH, f".//ul[@class='dropdown-city-list']/li[text()=' {desired_city} ']")
            city_element.click()
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Element not found, Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding element: {str(e)}")
            return None

    
    def search_for_text(self, search_text):
        """Inputs text into the search box and clicks the search button.

        Args:
            driver: The Selenium WebDriver instance.
            search_text: The text to enter into the search box.

        Returns:
            True if the search was initiated successfully, False otherwise.
        """
        try:
            # Locate the search input box
            input_box = self.driver.find_element(By.CSS_SELECTOR, ".input-wrap.input-wrap-text input.input")

            # Clear any existing text (optional, but good practice)
            input_box.clear()

            # Enter the search text
            input_box.send_keys(search_text)
            self._random_sleep(2,4)
            # Option 1: Click the "搜索" button (assuming it has a class or other identifiable attribute)
            search_button = self.driver.find_element(By.CSS_SELECTOR, ".search-btn")  #  Adapt this selector!
            search_button.click()

            # Option 2: Simulate pressing "Enter" in the input box (if that also triggers the search)
            # input_box.send_keys(Keys.ENTER)

            return True
        except Exception as e:
            print(f"Error during search: {e}")
            return False
    
    def get_full_select_url(self, root_url, menu_path, options_to_select):
        with open(menu_path,'r',encoding='utf-8') as f:
            data = json.load(f)

        url_tail = []
        for key, value in options_to_select.items():
            if len(value) == 0:
                continue
            else:
                subtitle = data[key]
                codes = []
                name = ""
                for element in value:
                    code = subtitle.get(element, "")
                    sep_code = code.split("-")
                    codes.append(sep_code[-1])
                    if name == "":
                        name = sep_code[-2]
                
                subtitle_code = "=".join([name,",".join(codes)])
                url_tail.append(subtitle_code)
        result = "&".join(url_tail)
        if root_url.endswith("?"):
            res_url = root_url + result
        else:
            res_url = root_url + "&" + result
        return res_url


    def close_login_interface(self):
        """
        close the login interface, rather than the crawler cannot click other btn
        """
        try:
            self._random_sleep(0,2)
            login_dialog = self.driver.find_element(By.CSS_SELECTOR, ".boss-login-dialog")
            close_logindialog = login_dialog.find_element(By.CSS_SELECTOR, "span")
            close_logindialog.click()
            return True
        except:
            logging.info("There is no login interface.")
            return None

    def login(self):
        try:
            header = self.find_element(By.ID, "header")
            header_login_btn = self.find_element(By.CSS_SELECTOR, ".btns", parent_element=header)
            login_btn = self.find_element(By.CSS_SELECTOR, "a", parent_element=header_login_btn)
            if_click = self.click_element(login_btn)
            # Find the login interface erea
            login_mid_interface = self.driver.find_element(By.CSS_SELECTOR, ".sms-form-wrapper")
            form_row = self.find_elements(By.CSS_SELECTOR, ".sms-form-row", parent_element=login_mid_interface)
            phone_row = form_row[0]
            passcode_row = form_row[-1]
            phone_box = self.find_element(By.CSS_SELECTOR, "input", parent_element=phone_row)
            phone_box.clear()
            # Enter the phone number
            phone_box.send_keys(self.login_phone)
            self._random_sleep(2,6)
            send_passcode_btn = self.find_element(By.CSS_SELECTOR, ".btn-sms",parent_element=passcode_row)
            self.click_element(send_passcode_btn)
            passcode = input("There is a human check, please pass the human check. Then, type in verification code:")
            # Enter the Verification Code
            passcode_box = self.find_element(By.CSS_SELECTOR, "input", parent_element=passcode_row)
            passcode_box.clear()
            passcode_box.send_keys(passcode)
            # Click the login button
            login_btn_erea = self.find_element(By.CSS_SELECTOR,".sms-form-btn",parent_element=login_mid_interface)
            _login_btn = self.find_element(By.CSS_SELECTOR,"button",parent_element=login_btn_erea)
            self._random_sleep(1,3)
            self.click_element(_login_btn)
            self.wait_for_page_load(self.long_timeout)
            return True
        except Exception as e:
            return False
        

    def search_jobs(self, url: str, query: str, location: str) -> List[Dict[str, Any]]:
        """
        Example method to search for jobs.
        
        Args:
            url: The job search website URL
            job_title: Job title to search for
            location: Location to search in
            
        Returns:
            List of job listings
        """
        # This is a placeholder implementation
        # You would need to adapt this to the specific website you're crawling
        
        if not self.navigate_to_url(url):
            return []
        
        # Example: Fill in search form
        try:
            ## location ##
            self.wait_for_page_load(self.long_timeout * 2)
            finished_search_city = self.search_city(location)
            ## query ##
            self._random_sleep(3,6)
            self.wait_for_page_load(self.long_timeout * 2)
            finished_search_text = self.search_for_text(query)
            input("If the page is visiable? Yes, please press \"ENTER\", No, please wait for the loading... >")
            url = self.driver.current_url
            options = {"求职类型":["全职"], "工作经验":[], "薪资待遇":[], "学历要求":["本科"], "公司规模":["10000人以上"], "融资阶段":[]} 
            new_url = self.get_full_select_url(url, self.select_menu_path, options)
            if not self.navigate_to_url(new_url):
                return []
            logging.info("Searching finished")
            self._random_sleep(2,4)
            try:
                self._random_sleep(0,2)
                login_dialog = self.driver.find_element(By.CSS_SELECTOR, ".boss-login-dialog")
                close_logindialog = login_dialog.find_element(By.CSS_SELECTOR, "span")
                close_logindialog.click()
            except:
                logging.info("There is no login interface.")
            
            # Extract job listings
            return self._extract_job_listings()
            
        except Exception as e:
            logger.error(f"Error during job search: {str(e)}")
            return []
    
    def _extract_job_listings(self) -> List[Dict[str, Any]]:
        """
        Extract job listings from the search results page.
        
        Returns:
            List of job listings
        """
        # This is a placeholder implementation
        # You would need to adapt this to the specific website you're crawling
        
        job_listings = []
        self.wait_for_page_load(self.long_timeout)
        # Example: Find all job cards
        job_cards = self.find_elements(By.CLASS_NAME, "job-card-wrapper")
        
        
        for card in tqdm(job_cards):
            try:
                left_card = self.find_element(By.CLASS_NAME, "job-card-left", parent_element=card)
                right_card = self.find_element(By.CLASS_NAME, "job-card-right", parent_element=card)
                # self._random_sleep(1,2)
                # Extract job details
                title_element = self.find_element(By.CLASS_NAME, "job-title", parent_element=left_card)
                subtitle_element = self.find_element(By.CLASS_NAME, "tag-list", parent_element=left_card)
                company_element = self.find_element(By.CLASS_NAME, "company-name", parent_element=right_card)
                company_sub_element = self.find_element(By.CLASS_NAME, "company-tag-list", parent_element=right_card)
                salary_element = self.find_element(By.CLASS_NAME, "salary", parent_element=left_card)
                contact_btn = self.find_element(By.CLASS_NAME, "info-public", parent_element=left_card)
                # self._random_sleep(1,2)
                link = self.extract_attribute(left_card,"href")
                title_text = self.extract_text(title_element) if title_element else ""
                subtitle_text = self.extract_text(subtitle_element) if title_element else ""
                self.extract_text(title_element) if title_element else ""
                company_sub = self.find_elements(By.CSS_SELECTOR, "li",parent_element=company_sub_element) if company_sub_element else ""
                if len(company_sub) == 2:
                    financing_stage = ""
                else:
                    financing_stage = self.extract_text(company_sub[1]) if company_sub_element else ""
                # self._random_sleep(1,2)
                job = {
                    "title": title_text.split("\n")[0] if title_element else "",
                    "company": {
                        "name": self.extract_text(company_element) if company_element else "",
                        "industry": self.extract_text(company_sub[0]) if company_sub_element else "",
                        "financing_stage": financing_stage,
                        "company_size": self.extract_text(company_sub[-1]) if company_sub_element else ""
                    },
                    "location": title_text.split("\n")[-1] if title_element else "",
                    "salary": self.extract_text(salary_element) if salary_element else "",
                    "experiences":subtitle_text.split("\n")[0] if subtitle_element else "",
                    "degree":subtitle_text.split("\n")[-1] if subtitle_element else "",
                    "url": link if link else "",
                    "contact_hr": contact_btn,
                }
                
                job_listings.append(job)
                
            except Exception as e:
                logger.error(f"Error extracting job listing: {str(e)}")
        
        return job_listings
    
    def click_page(self,button="next"):
        """Clicks the "next page" button.

        Args:
            driver: The Selenium WebDriver instance.

        Returns:
            True if the button was clicked successfully, False otherwise.
        """
        try:
            # Locate and click the "next page" button (assuming a common structure - adapt!)
            #  **This is an assumption - you MUST verify the correct selector!**
            next_page_element = WebDriverWait(self.driver, self.mid_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination-area"))
                )
            pagers = self.find_element(By.CSS_SELECTOR, ".pager", parent_element=next_page_element)
            if button == "next":
                button_element = self.find_element(By.CLASS_NAME, "ui-icon-arrow-right", parent_element=pagers)
            elif button.isdigit():
                buttons = self.find_elements(By.CSS_SELECTOR, "a", parent_element=pagers)
                buttons_elements = {btn.text:btn for btn in buttons}
                index = int(button)
                if index in buttons_elements:
                    button_element = buttons_elements[index]
                else:
                    logging.warning(f"the page you want to find (Page {index}) is not clickable!")
                    new_index = input(f"Available page index:{list(buttons_elements.keys())}, cannot choose none, please enter the page index >")
                    button_element = buttons_elements[new_index]
            self.click_element(button_element, 3)
            # next_button.click()
            return True
        except Exception as e:
            print(f"Error clicking next page button: {e}")
            return False


    def controlled_scroll_down(self, scroll_step=200, delay=0.1):
        """Scrolls down the page in steps with a delay, controlling the speed.

        Args:
            driver: The Selenium WebDriver instance.
            scroll_step: The number of pixels to scroll in each step.  Smaller values = slower scroll.
            delay: The time to wait between scroll steps, in seconds.  Larger values = slower scroll.
        """
        try:
            current_position = self.driver.execute_script("return window.pageYOffset;")
            max_height = self.driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
            logging.info("Scrolling......")
            while current_position < max_height:
                if current_position + scroll_step >= max_height:
                    self.driver.execute_script(f"window.scrollTo(0, {max_height});")
                    current_position = max_height
                else:
                    self.driver.execute_script(f"window.scrollTo(0, {current_position + scroll_step});")
                    current_position += scroll_step
                time.sleep(delay)

        except Exception as e:
            logging.warning(f"Error during controlled scroll: {e}")


    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_url: URL of the job listing
            
        Returns:
            Dictionary with job details
        """
        # This is a placeholder implementation
        # You would need to adapt this to the specific website you're crawling
        
        if not self.navigate_to_url(job_url):
            return {}
        try:
            job_details = {}

            return job_details
            
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            return {}
    
    def scan_page(self, scroll_step=250, delay=0.3):
        """
        1. crawl every job card in this page
        2. scroll the page down to the end (mimic the human action)
        """
        try:
            self.wait_for_page_load(self.mid_timeout)
            new_jobs = self._extract_job_listings()
            self.controlled_scroll_down(scroll_step=scroll_step, delay=delay)
        except Exception as e:
            logging.error(f"There is a problem with scanning the page. Error: {e}")
            return []
        return new_jobs
    