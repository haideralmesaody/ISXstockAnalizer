import logging
import time
from datetime import datetime
import pandas as pd
import pandas_ta as ta
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSignal
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from app_config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
from LoggerFunction import Logger  # Import your Logger class
from pandas import DataFrame
class DataFetcher(QObject):
    data_frame_ready_signal = pyqtSignal(DataFrame)
    def __init__(self, driver_path):
        super().__init__()
        self.driver_path = driver_path
        self.logger = Logger()

    def fetch_data(self, ticker, desired_rows):
        driver = None  # Initialize driver to None
        try:
            # Initialization and existing code
            self.logger.log_or_print("Attempting to allocate Selenium WebDriver resource...", level="INFO")
            URL = f'{BASE_URL}?currLanguage=en&companyCode={ticker}&activeTab=0'

            # Initialize Edge driver
            driver_service = Service(EDGE_DRIVER_PATH)
            driver = EdgeDriver(service=driver_service)
            self.logger.log_or_print("Successfully allocated Selenium WebDriver resource.", level="INFO")

            driver.get(URL)
            self.dismiss_alert_if_present(driver)

            # Adjust the value of the input field
            driver.execute_script('document.querySelector("#fromDate").value = "1/1/2010";')
            WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(lambda driver: driver.execute_script('return document.querySelector("#fromDate").value;') == "1/1/2010")

            # Find the button and click it
            update_button = driver.execute_script('return document.querySelector("#command > div.filterbox > div.button-all")')
            update_button.click()

            time.sleep(2)  # Wait for a couple of seconds after pressing the button

            # Wait for table to load
            self.wait_for_table_to_load(driver)
            
            df = self.initialize_dataframe()
            page_num = 1

            while len(df) < desired_rows:
                self.logger.log_or_print(f"Scraping page {page_num}...", level="INFO")
                df = self.extract_data_from_page(df, driver)

                if len(df) >= desired_rows:
                    break
                
                self.navigate_to_next_page(driver)
                page_num += 1
            df = df.sort_values(by='Date', ascending=True)

            # Compute the actual change and change% based on the Close prices
            df['Change'] = df['Close'].diff()
            df['Change%'] = df['Change'] / df['Close'].shift(1) * 100
            # Round the values to two decimal places
            df['Change'] = df['Change'].round(2)
            df['Change%'] = df['Change%'].round(2)
           
            self.logger.log_or_print(f"Data fetching completed. {len(df)} rows fetched.", level="INFO")
            self.data_frame_ready_signal.emit(df)
            return df

        except Exception as e:
            # Log the exact exception details
            self.logger.log_or_print(f"An error occurred while processing ticker {ticker}: {str(e)}", level="ERROR", exc_info=True)
            
            # Log the current state of the WebDriver
            current_url = driver.current_url
            self.logger.log_or_print(f"WebDriver state at error: Current URL = {current_url}", level="DEBUG")
            # Optional: Save a screenshot to see where the browser is when the error occurs
            # driver.save_screenshot('error_screenshot.png')
            # self.logger.log_or_print("Saved a screenshot as error_screenshot.png for debugging.", level="DEBUG")
            
            return None

        finally:
            if driver:
                self.release_webdriver_resource(driver)


    def initialize_dataframe(self):
        # Initialize DataFrame
        df = pd.DataFrame(columns=[
            "Date", "Close", "Open", "High", "Low", "Change", "Change%", "T.Shares", "Volume", "No. Trades"
        ])
        return df

    def wait_for_table_to_load(self, driver):
        try:
            WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dispTable")))
        except TimeoutException:
            self.logger.log_or_print("Table did not load in time.", level="ERROR")
            raise
                            

    def extract_data_from_page(self, df, driver):
        """Extract data from the current web page and append to DataFrame."""
        try:
            self.logger.log_or_print("Extracting data from current page...", level="INFO")

            table_html = driver.execute_script('return document.querySelector("#dispTable").outerHTML;')
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')

            # Extracting data and appending to DataFrame
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                date = datetime.strptime(cols[9].text.strip(), '%d/%m/%Y').date()
                open_price = float(cols[8].text.strip().replace(',', ''))
                high = float(cols[7].text.strip().replace(',', ''))
                low = float(cols[6].text.strip().replace(',', ''))
                close = float(cols[5].text.strip().replace(',', ''))
                change = float(cols[4].text.strip().replace(',', ''))
                change_percent = float(cols[3].text.strip().replace('%', '').replace(',', ''))
                t_shares = int(cols[2].text.strip().replace(',', ''))
                volume = int(cols[1].text.strip().replace(',', ''))
                no_trades = int(cols[0].text.strip().replace(',', ''))

                row_data = [date, open_price, high, low, close, change, change_percent, t_shares, volume, no_trades]
                df.loc[len(df)] = row_data
            
            self.logger.log_or_print("Data extraction successful.", level="INFO")
            return df
            
        except Exception as e:
            self.logger.log_or_print(f"An error occurred while extracting data from the page: {str(e)}", level="ERROR", exc_info=True)
            return df  # Return the DataFrame as is
            
        except Exception as e:
            self.logger.log_or_print(f"An error occurred while extracting data from the page: {str(e)}", level="ERROR", exc_info=True)
            return df  # Return the DataFrame as is

    def navigate_to_next_page(self, driver):
        """Navigate to the next page of data."""
        try:
            self.logger.log_or_print("Navigating to the next page...", level="INFO")
            
            next_page_btn_selector = "#ajxDspId > div > span.pagelinks > a:nth-child(11)"
            next_page_btn = driver.find_element(By.CSS_SELECTOR, next_page_btn_selector)
            
            if next_page_btn:
                next_page_btn.click()
                WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dispTable")))
                self.logger.log_or_print("Successfully navigated to the next page.", level="INFO")
            else:
                self.logger.log_or_print("Next page button not found.", level="WARNING")
                
        except Exception as e:
            self.logger.log_or_print(f"An error occurred while navigating to the next page: {str(e)}", level="ERROR", exc_info=True)
    def release_webdriver_resource(self, driver):
        self.logger.log_or_print("Attempting to release Selenium WebDriver resource...", level="INFO")
        driver.quit()
        self.logger.log_or_print("Successfully released Selenium WebDriver resource.", level="INFO")
        
    def dismiss_alert_if_present(self, driver):
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            self.logger.log_or_print("Alert found and dismissed.", level="INFO")
        except NoAlertPresentException:
            self.logger.log_or_print("No alert was present.", level="INFO")            