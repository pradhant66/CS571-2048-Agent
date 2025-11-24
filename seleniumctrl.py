# -*- coding: utf-8 -*-
"""
Selenium-based browser control for 2048.
Automatically launches a browser and navigates to the 2048 game.
"""

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class SeleniumControl(object):
    """
    Control a browser using Selenium.
    Automatically launches Chrome and navigates to the 2048 game.
    
    This is a drop-in replacement for ChromeDebuggerControl.
    """
    
    def __init__(self, url="https://play2048.co/", headless=False, browser="chrome"):
        """
        Initialize Selenium browser control.
        
        Args:
            url: URL of the 2048 game (default: https://play2048.co/)
            headless: Whether to run browser in headless mode (default: False)
            browser: Browser to use - "chrome" or "firefox" (default: "chrome")
        """
        if not SELENIUM_AVAILABLE:
            raise NotImplementedError(
                "Selenium library not available.\n"
                "Please install it (pip install selenium) then try again."
            )
        
        self.url = url
        self.driver = None
        
        # Create browser instance
        if browser.lower() == "chrome":
            self._init_chrome(headless)
        elif browser.lower() == "firefox":
            self._init_firefox(headless)
        else:
            raise ValueError(f"Unsupported browser: {browser}. Use 'chrome' or 'firefox'.")
        
        # Navigate to the game
        print(f"Navigating to {url}...")
        self.driver.get(url)
        
        # Wait for the game to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "game-container"))
            )
            print("Game loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not detect game container: {e}")
            print("The page may still be loading or the game structure may be different.")
    
    def _init_chrome(self, headless):
        """Initialize Chrome browser."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Try to create driver (will use chromedriver from PATH or webdriver-manager if available)
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            # If chromedriver is not in PATH, try using webdriver-manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                raise Exception(
                    "ChromeDriver not found. Please either:\n"
                    "1. Install chromedriver and add it to PATH, or\n"
                    "2. Install webdriver-manager: pip install webdriver-manager"
                ) from e
    
    def _init_firefox(self, headless):
        """Initialize Firefox browser."""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        
        firefox_options = FirefoxOptions()
        if headless:
            firefox_options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Firefox(options=firefox_options)
        except Exception as e:
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
            except ImportError:
                raise Exception(
                    "GeckoDriver not found. Please either:\n"
                    "1. Install geckodriver and add it to PATH, or\n"
                    "2. Install webdriver-manager: pip install webdriver-manager"
                ) from e
    
    def execute(self, cmd):
        """
        Execute JavaScript code in the browser.
        
        Args:
            cmd: JavaScript code to execute
            
        Returns:
            Result of the JavaScript evaluation
        """
        if self.driver is None:
            raise Exception("Browser driver not initialized")
        
        # Selenium's execute_script automatically returns the last expression
        # For statements, we need to wrap them properly
        cmd_stripped = cmd.strip()
        
        # If it's a multi-line block or ends with semicolon, it's likely a statement
        # For single expressions, Selenium will return the value automatically
        if '\n' in cmd or cmd_stripped.endswith(';'):
            # Multi-line or statement - execute as-is
            result = self.driver.execute_script(cmd)
            return result
        else:
            # Single expression - wrap to ensure we get the return value
            # Use parentheses to handle edge cases like object property access
            try:
                result = self.driver.execute_script(f"return ({cmd})")
                return result
            except Exception:
                # If wrapping fails, try without parentheses
                try:
                    result = self.driver.execute_script(f"return {cmd}")
                    return result
                except Exception:
                    # Last resort: execute as statement
                    result = self.driver.execute_script(cmd)
                    return result
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes browser."""
        self.close()
        return False

