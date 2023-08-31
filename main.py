# Standard Libraries
import logging
import os
import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import pyqtSignal
# Third-party Libraries
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QSizePolicy,
                             QSpinBox, QVBoxLayout, QWidget)
from bs4 import BeautifulSoup
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from data_fetcher import DataFetcher
from data_processing import DataProcessing
from PyQt5 import QtWidgets
import traceback
# Configure logging
from config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
def setup_logging():
    logging.basicConfig(**LOGGING_CONFIG)

from LoggerFunction import Logger
from config import DEBUG
# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

class App:
    def __init__(self, main_logic):
        self.logger = Logger(DEBUG)  # Initialize the logger
        self.logger.log_or_print("App: Initializing...", level="INFO", module="App")
        
        self.main_logic = main_logic
        self.setup_ui()
        
        self.logger.log_or_print("App: Initialized.", level="INFO", module="App")

    def run(self):
        self.logger.log_or_print("App: Running GUI.", level="INFO", module="App")
        self.gui.show()

class MainGUI(QMainWindow):
        def __init__(self, main_logic=None):
            try:
                self.some_var = None  # Initialize all class variables here
                self.logger = Logger(DEBUG)  # Initialize the logger
                self.logger.log_or_print("MainGUI: Initializing...", level="DEBUG", module="MainGUI")
                
                super(MainGUI, self).__init__()
                self.main_logic = main_logic
                
                # Rest of your existing code here...
              
                self.logger.log_or_print("MainGUI: Initialized.", level="DEBUG", module="MainGUI")
                self.initialize()
            except Exception as e:
                
                logger.log_or_print(f"An unexpected error occurred in main: {str(e)}. Stack Trace: {traceback.format_exc()}", level="ERROR", module="Main")
                raise  # re-raise the exception for higher-level handling

        def initialize(self):
            self.logger.log_or_print("MainGUI: Initializing...", level="INFO", module="MainGUI")
            self.logger.log_or_print("MainGUI: About to initialize UI.", level="DEBUG", module="MainGUI")
            try:
                self.logger.log_or_print("About to call setup_ui...", level="DEBUG", module="MainGUI")
                self.setup_ui()
                self.logger.log_or_print("Successfully called setup_ui.", level="DEBUG", module="MainGUI")
                self.logger.log_or_print("About to call connect_buttons...", level="DEBUG", module="MainGUI")
                self.connect_buttons()
                self.logger.log_or_print("Successfully called connect_buttons.", level="DEBUG", module="MainGUI")
                self.logger.log_or_print("MainGUI: UI Initialized.", level="INFO", module="MainGUI")
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in initialize: {str(e)}", level="ERROR", module="MainGUI")
                self.statusBar().showMessage("An unexpected error occurred. Check the log for details.")
            
        def setup_ui(self):
            try:
                self.logger.log_or_print("MainGUI: Setting up UI...", level="INFO", module="MainGUI")
                
                # Initialize Widgets
                self.initialize_widgets()
                
                # Setup Layouts
                self.setup_layouts()
                
                # Assemble Final UI
                self.assemble_ui()
                self.logger.log_or_print("MainGUI: UI set up successfully.", level="INFO", module="MainGUI")
            except AttributeError as e:
                self.logger.log_or_print(f"AttributeError in setup_ui: {e}", level="ERROR", module="MainGUI")
                raise
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_ui: {str(e)}", level="ERROR", module="MainGUI")
                raise


        def initialize_widgets(self):
            try:
                self.status_label = QLabel(self)
                self.ticker_input = QLineEdit()
                self.rows_label = QLabel("Number of rows:")
                self.row_spin_box = QSpinBox()
                self.row_spin_box.setMinimum(1)
                self.row_spin_box.setMaximum(1000)
                self.row_spin_box.setValue(300)
                self.sma_checkbox = QCheckBox("Show SMA")
                self.rsi_checkbox = QCheckBox("Show RSI14")
                self.stoch_checkbox = QCheckBox("Show Stoch(9,6)")
                self.sma_period_spinbox = QSpinBox()
                self.sma_period_spinbox.setMinimum(1)
                self.sma_period_spinbox.setMaximum(200)
                self.sma_period_spinbox.setValue(10)
                self.rsi_label = QLabel("RSI: -")
                self.stoch_label = QLabel("Stoch: -")
                self.rsi_state_label = QLabel(self)
                self.rsi_status_label = QLabel(self)
                self.RSIDivergeRecommendation_label = QLabel(self)
                
                # Initialize Data Fetcher and Processor
                self.data_fetcher = DataFetcher(EDGE_DRIVER_PATH)
                self.data_processing = DataProcessing(self)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in initialize_widgets: {str(e)}", level="ERROR", module="MainGUI")
                raise
        def setup_layouts(self):
            try:
                main_layout = QHBoxLayout()
                self.splitter = QSplitter()

                # Left section
                self.left_widget = QWidget()
                left_layout = QVBoxLayout()
                self.left_widget.setLayout(left_layout)
                left_layout.addWidget(QLabel("Enter Ticker:"))
                left_layout.addWidget(self.ticker_input)
                left_layout.addWidget(self.rows_label)
                left_layout.addWidget(self.row_spin_box)
                left_layout.addWidget(self.sma_checkbox)
                left_layout.addWidget(self.rsi_checkbox)
                left_layout.addWidget(self.stoch_checkbox)
                self.start_button = QPushButton("Start")
                left_layout.addWidget(self.start_button)
                self.save_button = QPushButton("Save")
                left_layout.addWidget(self.save_button)
                self.splitter.addWidget(self.left_widget)

                # Middle section
                middle_widget = QWidget()
                middle_layout = QVBoxLayout()
                middle_widget.setLayout(middle_layout)
                self.setup_web_view(middle_layout)
                self.splitter.addWidget(middle_widget)

                # Right section
                self.right_widget = QWidget()
                right_layout = QVBoxLayout()
                self.right_widget.setLayout(right_layout)
                right_layout.addWidget(self.rsi_label)
                right_layout.addWidget(self.rsi_state_label)
                right_layout.addWidget(self.RSIDivergeRecommendation_label)
                right_layout.addWidget(self.stoch_label)
                self.splitter.addWidget(self.right_widget)

                main_layout.addWidget(self.splitter)
                central_widget = QWidget()
                central_widget.setLayout(main_layout)
                self.setCentralWidget(central_widget)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_layouts: {str(e)}", level="ERROR", module="MainGUI")
                raise

        def assemble_ui(self):
            try:
                if not hasattr(self, 'splitter'):
                    raise AttributeError("MainGUI object has no attribute 'splitter'")
                # Assuming that the width of the main window is available
                screen_width = self.width()
                self.splitter.setSizes([int(0.05 * screen_width), int(0.80 * screen_width), int(0.15 * screen_width)])
            except AttributeError as e:
                self.logger.log_or_print(f"AttributeError in assemble_ui: {e}", level="ERROR", module="MainGUI")
                raise
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in assemble_ui: {str(e)}", level="ERROR", module="MainGUI")
                raise         

        def connect_buttons(self):
            try:
                self.logger.log_or_print("MainGUI: Connecting buttons...", level="DEBUG", module="MainGUI")
                
                # Connect start_button to its slot
                self.start_button.clicked.connect(self.main_logic.start_fetching_data)  # same as previous

                # Connect save_button to its slot
                self.save_button.clicked.connect(self.main_logic.save_data_to_excel)  # same as previous

                # Connect checkboxes
                self.sma_checkbox.stateChanged.connect(self.trigger_plot)  # same as previous
                self.rsi_checkbox.stateChanged.connect(self.trigger_plot)  # same as previous
                self.stoch_checkbox.stateChanged.connect(self.trigger_plot)  # same as previous

                # Connect SpinBox
                self.sma_period_spinbox.valueChanged.connect(self.main_logic.recalculate_and_plot)  # same as previous

                self.logger.log_or_print("MainGUI: Buttons connected.", level="DEBUG", module="MainGUI")
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in connect_buttons: {str(e)}", level="ERROR", module="MainGUI")
                raise

        def trigger_plot(self):
            try:
                self.logger.log_or_print("MainGUI: Triggering plot...", level="DEBUG", module="MainGUI")
                self.main_logic.plot_chart()  # Delegate to MainLogic
                self.logger.log_or_print("MainGUI: Plot triggered.", level="DEBUG", module="MainGUI")
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in trigger_plot: {str(e)}", level="ERROR", module="MainGUI")
                raise

        # ------- UI Component Setup Methods --------
    
        def setup_top_layout(self, main_layout):
            try:
                """Set up the top layout containing input widgets."""
                top_layout = QHBoxLayout()
                self.ticker_input = QLineEdit()
                self.ticker_input.setPlaceholderText("Enter ticker")
                top_layout.addWidget(self.ticker_input)

                self.rows_label = QLabel("Number of rows:")
                top_layout.addWidget(self.rows_label)

                self.row_spin_box = QSpinBox()
                self.row_spin_box.setMinimum(1)
                self.row_spin_box.setMaximum(1000)
                self.row_spin_box.setValue(300)
                top_layout.addWidget(self.row_spin_box)

                self.sma_checkbox = QCheckBox("Show SMA")
                top_layout.addWidget(self.sma_checkbox)

                self.sma_period_label = QLabel("SMA Period:")
                top_layout.addWidget(self.sma_period_label)
                
                self.sma_period_spinbox = QSpinBox()
                self.sma_period_spinbox.setMinimum(1)
                self.sma_period_spinbox.setMaximum(100)
                self.sma_period_spinbox.setValue(10)
                top_layout.addWidget(self.sma_period_spinbox)

                # RSI Checkbox
                self.rsi_checkbox = QCheckBox("Show RSI14")
                top_layout.addWidget(self.rsi_checkbox)

                # Stochastic Oscillator Checkbox
                self.stoch_checkbox = QCheckBox("Show Stoch(9,6)")
                top_layout.addWidget(self.stoch_checkbox)

                main_layout.addLayout(top_layout)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_top_layout: {str(e)}", level="ERROR", module="MainGUI")
                raise 

        def setup_buttons_layout(self, main_layout):
            try:
                """Set up the layout for buttons."""
                buttons_layout = QHBoxLayout()

                start_button = QPushButton("Start")
                start_button.clicked.connect(self.start_fetching_data)
                buttons_layout.addWidget(start_button)

                save_button = QPushButton("Save")
                save_button.clicked.connect(self.save_data_to_excel)
                buttons_layout.addWidget(save_button)

                main_layout.addLayout(buttons_layout)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_buttons_layout: {str(e)}", level="ERROR", module="MainGUI")
                raise
        def setup_web_view(self, main_layout):
            try:
                """Set up the web view for displaying charts."""
                self.web_view = QWebEngineView()
                print("Web view initialized.")
                main_layout.addWidget(self.web_view, 1)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_web_view: {str(e)}", level="ERROR", module="MainGUI")
                raise
        def setup_status_label(self, main_layout):
            try:
                """Set up the status label."""
                self.status_label = QLabel("Status: Ready")
                self.status_label.setFixedHeight(25)
                main_layout.addWidget(self.status_label)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_status_label: {str(e)}", level="ERROR", module="MainGUI")
                raise
        def setup_customize_button(self, main_layout):
            try:
                """Set up the "Customize Appearance" button."""
                customize_button = QPushButton("Customize Appearance")
                customize_button.clicked.connect(self.data_processing.update_chart_appearance)
                main_layout.addWidget(customize_button)
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in setup_customize_button: {str(e)}", level="ERROR", module="MainGUI")
                raise            
        # ------- Data Fetching and Processing Methods --------



   
class MainLogic:
        def __init__(self, gui_instance=None, data_fetcher=None, data_processing=None):
            try:
                self.logger = Logger(DEBUG)  # Initialize the logger
                self.logger.log_or_print("MainLogic: Initializing...", level="DEBUG", module="MainLogic")
                
                self.gui = gui_instance
                self.data_fetcher = data_fetcher or DataFetcher(EDGE_DRIVER_PATH)  # Use the provided data_fetcher or create a new one
                self.data_processing = data_processing or DataProcessing(self.gui)
                
                self.logger.log_or_print("MainLogic: Initialized.", level="DEBUG", module="MainLogic")
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in MainLogic __init__: {str(e)}", level="ERROR", module="MainLogic")
                raise
        def start_fetching_data(self):
            self.logger.log_or_print("MainLogic: Starting data fetching...", level="DEBUG", module="MainLogic")
            self.logger.log_or_print(f"MainLogic: GUI instance in start_fetching_data: {self.gui}", level="DEBUG", module="MainLogic")
            try:
                self.logger.log_or_print("MainLogic: About to fetch data.", level="DEBUG", module="MainLogic")
                data_fetcher = self.gui.data_fetcher
                ticker = self.gui.ticker_input.text().strip()
                desired_rows = self.gui.row_spin_box.value()
                if not ticker:
                    raise ValueError("Ticker cannot be empty")

                logging.info(f"Processing ticker: {ticker}...")
                
                if ticker:
                    logging.info(f"Processing ticker: {ticker}...")
                    if self.gui is None or self.gui.data_fetcher is None:
                        raise AttributeError("GUI or DataFetcher instance is not initialized.")
                    
                    self.df = data_fetcher.fetch_data(ticker, desired_rows)
                    self.update_gui_dataframe()
                    print(f"MainLogic: Fetched data, DataFrame shape: {self.df.shape}, DataFrame columns: {self.df.columns}")
                    # Calculate the stochastic oscillator values and store them in the DataFrame
                    self.df = data_fetcher.calculate_stochastic_oscillator(self.df)
                    # After calculating Stochastic Oscillator and before plotting
                    self.df['%K'] = self.df['%K'].clip(lower=0, upper=100)
                    self.df['%D'] = self.df['%D'].clip(lower=0, upper=100)
                    
                    # Plotting the candlestick chart
                    self.gui.data_processing.plot_candlestick_chart(self.df)
                    # Get the last date's RSI value and interpret its status
                    rsi_value = self.df['RSI14'].iloc[-1]
                    rsi_status, rsi_description = self.gui.data_processing.interpret_rsi(rsi_value)

                    # Update the RSI status label and tooltip in the UI
                    self.gui.rsi_state_label.setText(f"RSI State: {rsi_status}")  
                    self.gui.rsi_state_label.setToolTip(rsi_description)

                    # Detect divergences
                    self.df = self.gui.data_processing.detect_divergences(self.df)

                    # Provide recommendation based on divergences
                    recommendation = self.gui.data_processing.provide_recommendation()

                    # Update the recommendation label in the UI
                    self.gui.RSIDivergeRecommendation_label.setText(f"RSI Divergence Detection: - {recommendation}")  
                    print("NaN values in df:", self.df.isna().sum())
                    print("Columns in the DataFrame in MainWindow after data fetching:")
                    print(self.df.columns)
                    
                    # Get the last date's RSI value and interpret its status
                    rsi_value = self.df['RSI14'].iloc[-1]
                    rsi_status, rsi_description = self.gui.data_processing.interpret_rsi(rsi_value)

                    # Update the status label in the UI
                    self.gui.rsi_status_label.setText(f"RSI ({rsi_value:.2f}): {rsi_status}")  
                    self.gui.rsi_status_label.setToolTip(rsi_description)  
                  
            except AttributeError as e:
                self.logger.log_or_print(f"AttributeError in start_fetching_data: {e}. GUI Instance: {self.gui}", level="ERROR", module="MainLogic")
                self.gui.statusBar().showMessage("An error occurred. Check the log for details.")
            except ValueError as e:
                self.logger.log_or_print(f"ValueError in start_fetching_data: {e}. GUI Instance: {self.gui}", level="ERROR", module="MainLogic")
                self.gui.statusBar().showMessage(str(e))
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in start_fetching_data: {e}. GUI Instance: {self.gui}", level="ERROR", module="MainLogic")
                self.gui.statusBar().showMessage("An unexpected error occurred. Check the log for details.")
            self.logger.log_or_print("MainLogic: Data fetching complete.", level="INFO", module="MainLogic")
        def plot_chart(self):
            try:
                if self.gui.df is not None:
                    self.logger.log_or_print("MainLogic: DataFrame is not None. Plotting chart.", level="DEBUG", module="MainLogic")
                    self.gui.data_processing.plot_candlestick_chart(self.gui.df)
                else:
                    self.logger.log_or_print("MainLogic: DataFrame is None. Skipping plot.", level="WARNING", module="MainLogic")
            except Exception as e:
                self.logger.log_or_print(f"An unexpected error occurred in plot_chart: {str(e)}", level="ERROR", module="MainLogic")
                raise
        def update_gui_dataframe(self):
            self.gui.df = self.df
        def recalculate_and_plot(self):
            self.logger.log_or_print("MainLogic: Recalculating and plotting...", level="INFO", module="MainLogic")

            try:
                if self.df is not None and not self.df.empty:
                    self.df = self.data_fetcher.calculate_sma(self.df.copy(), self.sma_period_spinbox.value()) # Recalculate SMA with the new period, using a copy to avoid side effects
                    self.update_gui_dataframe()
                    self.gui.data_processing.plot_candlestick_chart(self.df)  # Plot the updated chart
            except Exception as e:
                
                self.logger.log_or_print(f"An error occurred in recalculate_and_plot: {str(e)}", level="ERROR", module="MainLogic")
                self.statusBar().showMessage("An error occurred. Check the log for details.")

            self.logger.log_or_print("MainLogic: Data saved to Excel.", level="DEBUG", module="MainLogic")
         # ------- Chart Plotting and Visualization Methods --------
      
        def enable_chart_interactions(self):
            fig = go.Figure(data=[go.Candlestick(x=self.df['Date'],
                                                open=self.df['Open'],
                                                high=self.df['High'],
                                                low=self.df['Low'],
                                                close=self.df['Close'])])

            # Enable chart interactions
            fig.update_layout(
                xaxis=dict(rangeslider=dict(visible=False)),  # Disable range slider
                xaxis_rangeslider=dict(visible=True),  # Enable separate x-axis slider
                yaxis=dict(autorange=True, fixedrange=False),  # Allow y-axis zooming
                dragmode="zoom",  # Enable zooming
                showlegend=False  # Disable legend for simplicity
            )

            raw_html = fig.to_html(include_plotlyjs='cdn')
            self.web_view.setHtml(raw_html)

        def enable_data_point_highlight(self):
            fig = go.Figure(data=[go.Candlestick(x=self.df['Date'],
                                                open=self.df['Open'],
                                                high=self.df['High'],
                                                low=self.df['Low'],
                                                close=self.df['Close'])])

            # Enable data point highlight
            fig.update_layout(
                xaxis=dict(rangeslider=dict(visible=False)),
                xaxis_rangeslider=dict(visible=True),
                yaxis=dict(autorange=True, fixedrange=False),
                dragmode="zoom",
                showlegend=False,
                hovermode="x unified",  # Highlight data points on hover across all subplots
                hovertemplate="%{x}<br>Open: %{open}<br>Close: %{close}<extra></extra>",  # Custom hover template
            )

            raw_html = fig.to_html(include_plotlyjs='cdn')
            self.web_view.setHtml(raw_html)

        # ------- File Operation Methods --------

        def save_data_to_excel(self):
            """Save data to Excel file."""
            try:
                self.logger.log_or_print("save_data_to_excel: Method invoked.", level="INFO", module="save_data_to_excel")
                if self.df is not None:
                    self.logger.log_or_print("save_data_to_excel: DataFrame is not None.", level="INFO", module="save_data_to_excel")

                    # Get the current datetime
                    now = datetime.now()
                    print(f"save_data_to_excel: Current datetime is {now}.")  # Log current datetime
                    
                    # Format the datetime and combine with the ticker name to form the filename
                    ticker = self.gui.ticker_input.text().strip()  # Access ticker_input through gui
                    print(f"save_data_to_excel: Ticker obtained is {ticker}.")  # Log obtained ticker
                    
                    filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}.xlsx"
                    print(f"save_data_to_excel: Generated filename is {filename}.")  # Log generated filename
                    
                    with pd.ExcelWriter(filename, engine=EXCEL_ENGINE) as writer:
                        self.df.to_excel(writer, sheet_name='Sheet1', index=False)  # This already includes all columns, including RSI14
                        self.logger.log_or_print("Data successfully written to Excel.", level="INFO", module="MainLogic")
                    
                    
                    self.gui.status_label.setText("Data saved successfully.")
                else:
                    print("save_data_to_excel: DataFrame is None. No data to save.")  # DataFrame doesn't exist
                    self.gui.status_label.setText("No data available to save.")
            except Exception as e:
                print(f"save_data_to_excel: An exception occurred. Details: {str(e)}.")  # Exception details
                logging.error(f"An error occurred in save_data_to_excel: {str(e)}")
                self.gui.status_label.setText("An error occurred. Check the log for details.")

        
def link_gui_and_logic(gui, logic):
    gui.main_logic = logic
    logic.gui = gui

if __name__ == "__main__":
    try:
        logger = Logger(DEBUG)
        logger.log_or_print("Main: Starting application...", level="DEBUG", module="Main")
        
        app = QtWidgets.QApplication(sys.argv)

        logic = MainLogic()
        logger.log_or_print("Main: Created MainLogic instance.", level="DEBUG", module="Main")

        gui = MainGUI(main_logic=logic)
        logger.log_or_print("Main: Created MainGUI instance.", level="DEBUG", module="Main")

        link_gui_and_logic(gui, logic)
        logger.log_or_print("Main: Linked GUI and Logic.", level="DEBUG", module="Main")

        gui.initialize()
        logger.log_or_print("Main: Initialized GUI.", level="DEBUG", module="Main")

        gui.show()
        logger.log_or_print("Main: Displayed GUI.", level="DEBUG", module="Main")

        sys.exit(app.exec_())
        logger.log_or_print("Main: Application started.", level="DEBUG", module="Main")
    except Exception as e:
        
        logger.log_or_print(f"An unexpected error occurred in main: {str(e)}. Stack Trace: {traceback.format_exc()}", level="ERROR", module="Main")
        sys.exit(1)