# config.py
import os
# Logging Configuration
LOGGING_CONFIG = {
    'filename': 'app.log',
    'level': 'ERROR',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}
import logging
from config import LOGGING_CONFIG

logging.basicConfig(**LOGGING_CONFIG)
current_directory = os.path.dirname(os.path.abspath(__file__))
# Edge Driver Configuration
EDGE_DRIVER_PATH = os.path.join(current_directory, 'msedgedriver.exe')

# URL Configuration
BASE_URL = 'http://www.isx-iq.net/isxportal/portal/companyprofilecontainer.html'
DEFAULT_DATE = "06/10/2010"

# Table Configuration
TABLE_SELECTOR = "#dispTable"

# WebDriver Wait Configuration
WEBDRIVER_WAIT_TIME = 10

# Data Fetching Configuration
DEFAULT_SMA_PERIOD = 10
DEFAULT_ROW_COUNT = 300

# Excel Configuration
EXCEL_ENGINE = 'openpyxl'

# Add any other constants or configurations that might be useful for your application here.
