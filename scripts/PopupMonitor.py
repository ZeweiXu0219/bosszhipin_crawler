import time
import random
import logging

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

class PopupMonitor:
    def __init__(self, driver, url=None):
        self.driver = driver
        if url:
            self.driver.get(url)
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PopupMonitor')
        
    def _random_sleep(self, min_seconds, max_seconds):
        """随机等待一段时间，模拟人类行为"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def close_login_popup(self):
        """关闭登录弹窗的方法"""
        try:
            self._random_sleep(0, 2)
            login_dialog = self.driver.find_element(By.CSS_SELECTOR, ".boss-login-dialog")
            close_logindialog = login_dialog.find_element(By.CSS_SELECTOR, "span")
            close_logindialog.click()
            self.logger.info("登录弹窗已关闭")
            return True
        except Exception as e:
            self.logger.info("没有检测到登录弹窗或关闭失败: %s", str(e))
            return False
    
    def monitor_popup_loop(self, interval=2, max_duration=None):
        """使用简单循环方法监控弹窗
        
        Args:
            interval: 检查间隔时间(秒)
            max_duration: 最大监控时间(秒)，None表示无限监控
        """
        start_time = time.time()
        self.logger.info("开始监控登录弹窗...")
        
        try:
            while True:
                # 检查是否已超过最大监控时间
                if max_duration and (time.time() - start_time > max_duration):
                    self.logger.info(f"已达到最大监控时间({max_duration}秒)，停止监控")
                    break
                
                # 检查弹窗是否存在
                try:
                    login_dialog = self.driver.find_element(By.CSS_SELECTOR, ".boss-login-dialog")
                    if login_dialog.is_displayed():
                        self.close_login_popup()
                except NoSuchElementException:
                    pass  # 弹窗不存在，继续监控
                
                # 等待一段时间再次检查
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("监控被手动中断")
    
    def monitor_popup_wait(self, check_interval=5, timeout=3):
        """使用WebDriverWait方法监控弹窗
        
        Args:
            check_interval: 两次检查之间的间隔时间(秒)
            timeout: 每次等待的超时时间(秒)
        """
        self.logger.info("开始监控登录弹窗(使用WebDriverWait)...")
        
        try:
            while True:
                try:
                    # 使用较短的超时时间等待弹窗出现
                    login_dialog = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".boss-login-dialog"))
                    )
                    # 弹窗出现，关闭它
                    self.close_login_popup()
                except TimeoutException:
                    # 超时意味着在指定时间内没有找到弹窗，继续等待
                    self.logger.debug(f"在{timeout}秒内未检测到弹窗")
                
                # 等待一段时间再次检查
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("监控被手动中断")
    
    def monitor_popup_mutation_observer(self, check_interval=0.5):
        """使用MutationObserver(JavaScript)方法监控弹窗
        
        Args:
            check_interval: JavaScript检测到弹窗后，Selenium检查的间隔时间(秒)
        """
        self.logger.info("开始监控登录弹窗(使用MutationObserver)...")
        
        # 注入JavaScript代码来监听DOM变化
        js_code = """
        // 创建一个存储监听器的变量，以便之后可以断开连接
        window.popupObserver = new MutationObserver(function(mutations) {
            // 检查是否有登录弹窗出现
            var loginPopup = document.querySelector('.boss-login-dialog');
            if (loginPopup && loginPopup.style.display !== 'none') {
                // 通知Selenium弹窗已出现（设置一个标记）
                document.body.setAttribute('data-popup-detected', 'true');
            }
        });
        
        // 配置监听器
        window.popupObserver.observe(document.body, {
            childList: true,   // 监视子节点的添加或删除
            subtree: true,     // 监视所有后代节点
            attributes: true,  // 监视属性变化
            attributeFilter: ['style', 'class']  // 只监视样式和类的变化
        });
        """
        
        # 执行JavaScript代码
        self.driver.execute_script(js_code)
        
        try:
            while True:
                # 检查JavaScript是否检测到弹窗
                popup_detected = self.driver.execute_script(
                    "return document.body.getAttribute('data-popup-detected') === 'true'"
                )
                
                if popup_detected:
                    # 重置标记
                    self.driver.execute_script("document.body.removeAttribute('data-popup-detected')")
                    # 关闭弹窗
                    self.close_login_popup()
                
                # 适当休眠
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            # 清理：断开MutationObserver连接
            self.driver.execute_script("if(window.popupObserver) window.popupObserver.disconnect();")
            self.logger.info("监控被手动中断")
        except Exception as e:
            self.logger.error(f"监控过程中发生错误: {str(e)}")
            # 确保断开MutationObserver连接
            self.driver.execute_script("if(window.popupObserver) window.popupObserver.disconnect();")
    
    def stop_monitoring(self):
        """停止所有监控活动并清理资源"""
        try:
            # 尝试断开可能存在的MutationObserver
            self.driver.execute_script("if(window.popupObserver) window.popupObserver.disconnect();")
        except:
            pass
        self.logger.info("监控已停止")
