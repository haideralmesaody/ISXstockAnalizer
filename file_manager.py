import pandas as pd
from datetime import datetime
from app_config import EXCEL_ENGINE
from LoggerFunction import Logger
class FileManager:
    
    def __init__(self):
        self.logger = Logger()

    def save_data_to_excel(self, df, ticker):
        """Save data to Excel file."""
        try:
            if self.logger:
                self.logger.log_or_print("save_data_to_excel: Method invoked.", level="INFO", module="FileManager")
            
            if df is not None:
                if self.logger:
                    self.logger.log_or_print("save_data_to_excel: DataFrame is not None.", level="INFO", module="FileManager")

                # Get the current datetime
                now = datetime.now()

                # Format the datetime and combine with the ticker name to form the filename
                filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}.xlsx"
                
                with pd.ExcelWriter(filename, engine=EXCEL_ENGINE) as writer:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    
                if self.logger:
                    self.logger.log_or_print("Data successfully written to Excel.", level="INFO", module="FileManager")
                
                return True
            else:
                if self.logger:
                    self.logger.log_or_print("save_data_to_excel: DataFrame is None. No data to save.", level="ERROR", module="FileManager")
                return False
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(f"save_data_to_excel: An exception occurred. Details: {str(e)}.", level="ERROR", module="FileManager")
            return False
