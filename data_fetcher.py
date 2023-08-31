import logging
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException
from config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
from LoggerFunction import Logger  # Import your Logger class
class DataFetcher:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.logger = Logger()

    def fetch_data(self, ticker, desired_rows):
                """Fetch and process data from the website."""
                try:
                    self.logger.log_or_print("Attempting to allocate Selenium WebDriver resource...", level="INFO")
                    URL = f'{BASE_URL}?currLanguage=en&companyCode={ticker}&activeTab=0'

                    # Initialize Edge driver
                    driver_service = Service(EDGE_DRIVER_PATH)
                    driver = EdgeDriver(service=driver_service)
                    self.logger.log_or_print("Successfully allocated Selenium WebDriver resource.", level="INFO")

                    driver.get(URL)
                    # Check for the presence of an alert and dismiss it
                    try:
                        alert = driver.switch_to.alert
                        alert.dismiss()
                        self.logger.log_or_print("Alert found and dismissed.", level="INFO")
                    except NoAlertPresentException:
                        self.logger.log_or_print("No alert was present.", level="INFO")
                        pass  # No alert was present
                    # Adjust the value of the input field
                    driver.execute_script('document.querySelector("#fromDate").value = "1/1/2010";')

                    # Wait for the change to take effect (you can adjust the waiting time as per your needs)
                    WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(lambda driver: driver.execute_script('return document.querySelector("#fromDate").value;') == "1/1/2010")

                    # Find the button using the provided XPath and click it
                    update_button = driver.execute_script('return document.querySelector("#command > div.filterbox > div.button-all")')
                    update_button.click()
                    # Wait for a couple of seconds after pressing the button
                    time.sleep(2)
                    # Wait for table to load
                    self.logger.log_or_print("Waiting for table to load...", level="INFO")
                    WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dispTable")))

                    # Initialize DataFrame
                    df = pd.DataFrame(columns=[
                        "Date", "Close", "Open", "High", "Low", "Change", "Change%", "T.Shares", "Volume", "No. Trades"
                    ])
                    #Calculating SMA
                    sma_period = DEFAULT_SMA_PERIOD  # Example period for SMA
                    page_num = 1
                    while len(df) < desired_rows:
                        self.logger.log_or_print(f"Scraping page {page_num}...", level="INFO")
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
                       
                        if len(df) >= desired_rows:
                            break

                        # Navigate to the next pageit
                        next_page_btn_selector = "#ajxDspId > div > span.pagelinks > a:nth-child(11)"
                        next_page_btn = driver.find_element(By.CSS_SELECTOR, next_page_btn_selector)
                        if next_page_btn:
                            next_page_btn.click()
                            WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dispTable")))

                        page_num += 1
                    #Calculating SMA
                    df = self.calculate_sma(df, sma_period)
                    df = df.sort_values(by='Date', ascending=True)
                    # Calculate RSI14 and add it to the DataFrame
                    
                    df['RSI14'] = self.calculate_rsi(df)
                    df = self.calculate_stochastic_oscillator(df)
                    self.logger.log_or_print(f"Data fetching completed. {len(df)} rows fetched.", level="INFO")
                    return df  # Return the DataFrame
                except UnexpectedAlertPresentException:
                    alert = driver.switch_to.alert
                    alert.accept()
                    self.logger.log_or_print("Alert accepted and retrying data fetching.", level="WARNING")
                    return self.fetch_data(ticker, desired_rows)

                except Exception as e:
                    self.logger.log_or_print(f"An error occurred while processing ticker {ticker}", level="ERROR", exc_info=True)
                    return None

                finally:
                    if driver:
                        self.logger.log_or_print("Attempting to release Selenium WebDriver resource...", level="INFO")
                        driver.quit()
                        self.logger.log_or_print("Successfully released Selenium WebDriver resource.", level="INFO")
                            

    def calculate_sma(self, data_frame, sma_period):
                """Calculate simple moving averages."""
                try:
                    self.logger.log_or_print("Starting SMA calculation...", level="INFO")
                    # Ensure the data_frame is sorted in ascending order by date
                    data_frame = data_frame.sort_values(by='Date', ascending=True)

                    # Calculate the SMA using the rolling window method
                    data_frame['SMA'] = data_frame['Close'].rolling(window=sma_period).mean()
                    data_frame['SMA50'] = data_frame['Close'].rolling(window=50).mean()
                    data_frame['SMA200'] = data_frame['Close'].rolling(window=200).mean()
                    self.logger.log_or_print("SMA calculation completed successfully.", level="INFO")
                    return data_frame
                except Exception as e:
                    self.logger.log_or_print(f"An error occurred in calculate_sma: {str(e)}", level="ERROR", exc_info=True)
    def calculate_rsi(self, data_frame, period=14):
                try:
                    self.logger.log_or_print("Starting RSI calculation...", level="INFO")
                    delta = data_frame['Close'].diff()
                    
                    # Separate the gains and losses into their own series
                    gain = (delta.where(delta > 0, 0)).fillna(0)
                    loss = (-delta.where(delta < 0, 0)).fillna(0)
                    
                    # Calculate the average gain and loss over the desired period
                    avg_gain = gain.rolling(window=period, min_periods=1).mean()
                    avg_loss = loss.rolling(window=period, min_periods=1).mean()
                    
                    # Calculate RS
                    rs = avg_gain / avg_loss
                    
                    # Calculate RSI
                    rsi = 100 - (100 / (1 + rs))
                    self.logger.log_or_print("RSI calculation completed successfully.", level="INFO")
                    return rsi
                except Exception as e:
                    self.logger.log_or_print(f"An error occurred in calculate_rsi: {str(e)}", level="ERROR", exc_info=True)
                    return None        # ... (rest of the method)
    def calculate_stochastic_oscillator(self, df, k_period=9, d_period=6):
        try:
            self.logger.log_or_print("Starting Stochastic Oscillator calculation...", level="INFO")

            # Calculate %K
            df['Lowest Low'] = df['Low'].rolling(window=k_period).min()
            df['Highest High'] = df['High'].rolling(window=k_period).max()
            df['%K'] = (df['Close'] - df['Lowest Low']) * 100 / (df['Highest High'] - df['Lowest Low'])

            # Calculate %D
            df['%D'] = df['%K'].rolling(window=d_period).mean()

            self.logger.log_or_print("Calculated %K and %D for Stochastic Oscillator.", level="INFO")

            # Drop temporary columns
            df.drop(['Lowest Low', 'Highest High'], axis=1, inplace=True)

            self.logger.log_or_print("Stochastic Oscillator calculation completed successfully.", level="INFO")
            return df
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in calculate_stochastic_oscillator: {str(e)}", level="ERROR", exc_info=True)
            return None