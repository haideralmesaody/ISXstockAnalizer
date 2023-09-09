import logging
import os
from datetime import datetime
from dateutil import tz
import time
import datetime
import pytz
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
        # Define the GMT+3 timezone
        gmt3 = tz.tzoffset('GMT+3', 3*3600)

        # Get the current date and time in GMT+3
        current_datetime = datetime.now(gmt3)
        current_date = current_datetime.date()
        
        self.logger.log_or_print(f"Starting data fetch for ticker {ticker} on {current_date}. Desired rows: {desired_rows}", level="INFO")

        driver = None  # Initialize driver to None
        filename = f"raw_{ticker}.csv"
        df = self.initialize_dataframe()
        df_existing = self.initialize_dataframe()
        df_temp = self.initialize_dataframe()
        try:
            if os.path.exists(filename):
                
                df_existing = pd.read_csv(filename)
                number_of_rows = df_existing.shape[0]
                self.logger.log_or_print(f"{filename} exists with {number_of_rows} rows.", level="INFO")
                self.logger.log_or_print(f"{filename}  exist!", level="INFO")
                self.logger.log_or_print(df.head(), level="INFO")
                # Ensure the 'Date' column is of datetime type
                df_existing['Date'] = pd.to_datetime(df_existing['Date'])
                # Get the maximum date
                max_date = df_existing['Date'].max().date()  # Convert to datetime.date
                difference_in_days = (current_date - max_date).days  # Calculate the difference in days
                self.logger.log_or_print(f"Max date from existing CSV: {max_date}. Difference in days: {difference_in_days}.", level="INFO")
                if difference_in_days > 20 or number_of_rows < desired_rows-20:# if the CSV is older than 10day the CSV or the number of rows are less than the desired rows be deleted and the to proceed normally to fetch the desired trading days
                    self.logger.log_or_print("Conditions met: Either the CSV is older than 10 days or number of rows is less than desired.", level="INFO")
                    os.remove(filename)
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
                    

                    page_num = 1

                    while len(df) < desired_rows:
                        self.logger.log_or_print(f"Scraping page {page_num}...", level="INFO")
                        df = self.extract_data_from_page(df, driver)
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.drop_duplicates(subset='Date', keep='first')
                        if len(df) >= desired_rows:
                            break
                        
                        self.navigate_to_next_page(driver)
                        page_num += 1
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values(by='Date', ascending=True)

                else: # if the CSV is freash fetch only the first page, to be modified to check for the number of rows
                    self.logger.log_or_print("Fetching only the first page since the CSV is fresh.", level="INFO")
                    os.remove(filename)
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
                    
                    df = self.extract_data_from_page(df, driver)
                    df_temp = pd.concat([df, df_existing], axis=0, ignore_index=True)
                    self.logger.log_or_print(f"After concatenation: {df_temp.shape[0]} rows.", level="INFO")
                    df=df_temp
                    df['Date'] = pd.to_datetime(df['Date'])
                    duplicate_dates = df[df.duplicated(subset='Date', keep='first')]['Date']
                    self.logger.log_or_print(f"Duplicate dates: {duplicate_dates.tolist()}", level="INFO")
                    df = df.drop_duplicates(subset='Date', keep='first')
                    self.logger.log_or_print(f"After dropping duplicates: {df.shape[0]} rows.", level="INFO")
                    df = df.sort_values(by='Date', ascending=False)
                    df=df.head(desired_rows)
                    df = df.sort_values(by='Date', ascending=True)
                    self.logger.log_or_print(f"After selecting top {desired_rows} rows: {df.shape[0]} rows.", level="INFO")
            else:
                self.logger.log_or_print(f"{filename} does not exist. Fetching new data...", level="INFO")
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
                

                page_num = 1

            while len(df) < desired_rows:
                self.logger.log_or_print(f"Scraping page {page_num}...", level="INFO")
                df_temp = self.extract_data_from_page(df, driver)  # Extract data into a temporary DataFrame

                # Append the temporary DataFrame to the main DataFrame
                df = pd.concat([df, df_temp], ignore_index=True)

                # Remove duplicates based on the 'Date' column
                df = df.drop_duplicates(subset='Date', keep='first')

                if len(df) >= desired_rows:
                    break

                self.navigate_to_next_page(driver)
                page_num += 1

            df = df.sort_values(by='Date', ascending=True)
            df = df.tail(desired_rows)  # This will keep only the latest 'desired_rows'

            # Compute the actual change and change% based on the Close prices
            df['Change'] = df['Close'].diff()
            df['Change%'] = df['Change'] / df['Close'].shift(1) * 100
            # Round the values to two decimal places
            df['Change'] = df['Change'].round(2)
            df['Change%'] = df['Change%'].round(2)
           
            self.logger.log_or_print(f"Data fetching completed. {len(df)} rows fetched.", level="INFO")
            self.data_frame_ready_signal.emit(df)
            filename = f"raw_{ticker}.csv"
            df.to_csv(filename, index=False)
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
