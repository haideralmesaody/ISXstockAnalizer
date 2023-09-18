from PyQt5.QtCore import QObject, pyqtSignal
from data_fetcher import DataFetcher
from data_visualizer import DataVisualizer  # Assuming you renamed the class
from LoggerFunction import Logger
from app_config import (EDGE_DRIVER_PATH, EXCEL_ENGINE, DEBUG)
import pandas as pd
from datetime import datetime
import os
from data_calculator import DataCalculator
from file_manager import FileManager
from PyQt5.QtCore import pyqtSlot
# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))


class MainLogic(QObject):
    data_fetched_signal = pyqtSignal(str)
    data_frame_ready_signal = pyqtSignal(pd.DataFrame)
    processed_data_signal = pyqtSignal(pd.DataFrame)
    indicator_values_updated_signal = pyqtSignal(dict)

    def __init__(self, main_gui=None):
        super().__init__()
        self.df = None  # Centralized DataFrame storage
        self.current_ticker = None  # Centralized ticker storage
        self.gui = main_gui
        self.logger = Logger(DEBUG)
        self.data_calculator = DataCalculator()
        # Connect the sma_calculated_signal to a slot
        self.data_calculator.sma_calculated_signal.connect(
            self.on_sma_calculated)
        # Connect the rsi_calculated_signal to a slot
        self.data_calculator.rsi_calculated_signal.connect(
            self.on_rsi_calculated)
        # Connect the stochastic_calculated_signal to a slot
        self.data_calculator.stochastic_calculated_signal.connect(
            self.on_stochastic_calculated)
        # Connect the cmf_calculated_signal to a slot
        self.data_calculator.cmf_calculated_signal.connect(
            self.on_cmf_calculated)
        # Connect the macd_calculated_signal to a slot
        self.data_calculator.macd_calculated_signal.connect(
            self.on_macd_calculated)
        # Connect the obv_calculated_signal to a slot
        self.data_calculator.obv_calculated_signal.connect(
            self.on_obv_calculated)
        main_gui.indicator_checkbox_changed_signal.connect(
            self.update_chart_with_indicators)
        self.gui.indicator_values_updated_signal.connect(
            self.gui.update_indicator_labels)
        self.indicator_values_updated_signal.connect(
            self.update_gui_labels_with_indicator_values)
        self.file_manager = FileManager()
        self.gui.save_data_signal.connect(self.save_data_slot)
        self.gui.generate_report_signal.connect(self.generate_report_slot)
        # Initialize and setup DataFetcher
        self.data_fetcher = DataFetcher(EDGE_DRIVER_PATH)
        self.data_fetcher.data_frame_ready_signal.connect(
            self.process_fetched_data)

        # Initialize and setup DataVisualizer
        self.data_visualizer = DataVisualizer()
        self.data_visualizer.chart_ready_signal.connect(self.gui.update_chart)

        # If a MainGUI instance is provided, connect its signals
        if main_gui:
            main_gui.start_data_fetching_signal.connect(self.fetch_data_slot)
            self.logger.log_or_print(
                "MainLogic: MainGUI signals connected.", level="DEBUG", module="MainLogic")

        self.logger.log_or_print(
            "MainLogic: Initialized.", level="DEBUG", module="MainLogic")

    def fetch_data_slot(self, ticker, desired_rows):

        try:
            df = self.data_fetcher.fetch_data(ticker, desired_rows)

            if df is not None:
                self.df = df  # Update the centralized DataFrame storage

                self.current_ticker = ticker  # Update the centralized ticker storage

                # Step 2: Handle the calculations directly after fetching
                self.handle_data_calculations()

                # Step 3: Process the data for visualization
                self.process_fetched_data(self.df)

                self.data_frame_ready_signal.emit(self.df)
            else:
                self.logger.log_or_print(
                    f"MainLogic: Fetched data for {ticker} is None. Skipping emission of data_frame_ready_signal signal.", level="WARNING", module="MainLogic")
        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error while fetching data: {str(e)}", level="ERROR", module="MainLogic")

    def process_fetched_data(self, df):
        try:
            fig = self.data_visualizer.plot_candlestick_chart(
                df)  # Use the correct method from DataVisualizer
            # Assuming update_chart expects a figure object
            self.gui.update_chart(fig)
        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error while process_fetched_data: {str(e)}", level="ERROR", module="MainLogic")

    def handle_data_calculations(self):
        try:
            if self.df is None:

                return

            self.logger.log_or_print(
                "MainLogic: Starting data calculations using the central DataFrame...", level="INFO", module="MainLogic")

            # Since calculations are done asynchronously and the central DataFrame is updated via signals,
            # we don't need to return and assign data in this method. Just initiate the calculations.

            # Start SMA calculation
            # This will emit the sma_calculated_signal
            self.data_calculator.calculate_sma(self.df)
            self.logger.log_or_print(
                "MainLogic: SMA calculation initiated.", level="INFO", module="MainLogic")

            # Start RSI calculation
            # This will emit the rsi_calculated_signal
            self.data_calculator.calculate_rsi(self.df)
            self.logger.log_or_print(
                "MainLogic: RSI calculation initiated.", level="INFO", module="MainLogic")

            # Start Stochastic Oscillator calculation
            self.data_calculator.calculate_stochastic_oscillator(
                self.df)  # This will emit the stochastic_calculated_signal
            self.logger.log_or_print(
                "MainLogic: Stochastic Oscillator calculation initiated.", level="INFO", module="MainLogic")
            # Start CMF calculation
            self.data_calculator.calculate_cmf(self.df)
            self.logger.log_or_print(
                "MainLogic: CMF calculation initiated.", level="INFO", module="MainLogic")

            # Start MACD calculation
            self.data_calculator.calculate_macd(self.df)
            self.logger.log_or_print(
                "MainLogic: MACD calculation initiated.", level="INFO", module="MainLogic")
            # Start OBV calculation
            self.data_calculator.calculate_obv(self.df)
            self.logger.log_or_print(
                "MainLogic: OBV calculation initiated.", level="INFO", module="MainLogic")
            latest_values = {
                'RSI_9': self.df['RSI_9'].iloc[-1] if 'RSI_9' in self.df.columns else None,
                'RSI_14': self.df['RSI_14'].iloc[-1] if 'RSI_14' in self.df.columns else None,
                'RSI_25': self.df['RSI_25'].iloc[-1] if 'RSI_25' in self.df.columns else None,
                'StochK': self.df['STOCHk_9_6_3'].iloc[-1] if 'STOCHk_9_6_3' in self.df.columns else None,
                'StochD': self.df['STOCHd_9_6_3'].iloc[-1] if 'STOCHd_9_6_3' in self.df.columns else None,
                'CMF_20': self.df['CMF_20'].iloc[-1] if 'CMF_20' in self.df.columns else None,
                'MACD_12_26_9': self.df['MACD_12_26_9'].iloc[-1] if 'MACD_12_26_9' in self.df.columns else None,
                'MACDs_12_26_9': self.df['MACDs_12_26_9'].iloc[-1] if 'MACDs_12_26_9' in self.df.columns else None,
                'OBV': self.df['OBV'].iloc[-1] if 'OBV' in self.df.columns else None,
            }

            self.logger.log_or_print(
                "Emitting indicator values update signal.", level="DEBUG", module="MainLogic")
            self.indicator_values_updated_signal.emit(latest_values)

            # At this point, once all calculations have been initiated, the central DataFrame `self.df` will be updated via signals
            # So, you don't need to explicitly assign `self.df = temp_df`. It's done in the signal handlers (slots).

        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error occurred during data calculations: {str(e)}", level="ERROR", module="MainLogic", exc_info=True)

    def save_data_slot(self):

        try:
            self.logger.log_or_print(
                f"MainLogic: Current ticker before check: {self.current_ticker}", level="DEBUG", module="MainLogic")
            if self.current_ticker is not None:  # Check if current_ticker has been set
                ticker = self.current_ticker
            else:
                self.logger.log_or_print(
                    f"MainLogic: Ticker not available for saving data.", level="WARNING", module="MainLogic")
                return
            self.logger.log_or_print(
                "MainLogic: About to fetch the latest DataFrame.", level="DEBUG", module="MainLogic")
            df = self.get_latest_dataframe()
            if df is not None:
                self.file_manager.save_data_to_excel(df, ticker)
                self.logger.log_or_print(
                    f"MainLogic: Data saved successfully for {ticker}.", level="INFO", module="MainLogic")
            else:
                self.logger.log_or_print(
                    f"MainLogic: No data available to save.", level="WARNING", module="MainLogic")
        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error while saving data to Excel: {str(e)}", level="ERROR", module="MainLogic")

    def get_latest_dataframe(self):
        try:

            return self.df

        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error in get_latest_dataframe: {str(e)}", level="ERROR", module="MainLogic")

    def on_sma_calculated(self, df):
        """
        Slot to handle the emitted DataFrame from the calculate_sma function.
        """

        if df is not None:
            self.df = df  # Update the centralized DataFrame storage

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from SMA calculation.", level="ERROR", module="MainLogic")

    def on_rsi_calculated(self, df):

        if df is not None:
            self.df = df

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from RSI calculation.", level="ERROR", module="MainLogic")

    def on_stochastic_calculated(self, df):

        if df is not None:
            self.df = df

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from Stochastic Oscillator calculation.", level="ERROR", module="MainLogic")

    def update_chart_with_indicators(self, active_indicators):
        if self.df is not None:
            fig = self.data_visualizer.plot_candlestick_chart(
                self.df, indicators=active_indicators)

            self.gui.update_chart(fig)
        else:
            self.logger.log_or_print(
                "MainLogic: DataFrame is None, cannot update chart.", level="WARNING", module="MainLogic")

    def on_cmf_calculated(self, df):
        self.logger.log_or_print(
            "MainLogic: Receiving CMF calculated DataFrame...", level="DEBUG", module="MainLogic")
        if df is not None:
            self.df = df

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from CMF calculation.", level="ERROR", module="MainLogic")

    def on_macd_calculated(self, df):

        if df is not None:
            self.df = df

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from MACD calculation.", level="ERROR", module="MainLogic")

    def on_obv_calculated(self, df):

        if df is not None:
            self.df = df

        else:
            self.logger.log_or_print(
                "MainLogic: Received None DataFrame from OBV calculation.", level="ERROR", module="MainLogic")

    def update_gui_labels_with_indicator_values(self, latest_values):
        self.gui.update_indicator_labels(latest_values)

    @pyqtSlot()
    def generate_report_slot(self):
        try:
            # Fetch the latest dataframe
            df = self.get_latest_dataframe()
            if df is not None and self.current_ticker is not None:
                # Generate the report using FileManager
                success = self.file_manager.generate_report(
                    df, self.current_ticker)
                if success:
                    self.logger.log_or_print(
                        f"MainLogic: Report generated successfully for {self.current_ticker}.", level="INFO", module="MainLogic")
                else:
                    self.logger.log_or_print(
                        f"MainLogic: Failed to generate report for {self.current_ticker}.", level="ERROR", module="MainLogic")
            else:
                self.logger.log_or_print(
                    f"MainLogic: No data available to generate report.", level="WARNING", module="MainLogic")
        except Exception as e:
            self.logger.log_or_print(
                f"MainLogic: Error while generating report: {str(e)}", level="ERROR", module="MainLogic")
