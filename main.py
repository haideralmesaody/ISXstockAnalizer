# Standard Libraries
import logging
import os
import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import QSplitter
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
# Configure logging
from config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
logging.basicConfig(**LOGGING_CONFIG)

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

class App:
    def __init__(self, main_logic):
        print("App: Initializing...")
        self.main_logic = main_logic
        self.setup_ui()
        print("App: Initialized.")

    def run(self):
        self.gui.show()

class MainGUI(QMainWindow):
        def __init__(self, main_logic=None):
            super(MainGUI, self).__init__()
            self.main_logic = main_logic

        def initialize(self):
            print("MainGUI: Initializing UI...")
            self.setup_ui()
            self.connect_buttons()
            
            print("MainGUI: UI Initialized.")
            
        def setup_ui(self):
            # Initialize the widgets
            print("MainGUI: Setting up UI...")
            self.status_label = QLabel(self)

            self.ticker_input = QLineEdit()
            self.rows_label = QLabel("Number of rows:")
            self.row_spin_box = QSpinBox()
            self.row_spin_box.setMinimum(1)
            self.row_spin_box.setMaximum(1000)
            self.row_spin_box.setValue(300)
            self.sma_checkbox = QCheckBox("Show SMA")
            self.rsi_checkbox = QCheckBox("Show RSI14")  # Initializing the rsi_checkbox
            self.stoch_checkbox = QCheckBox("Show Stoch(9,6)")  # Initializing the stoch_checkbox
            self.sma_period_spinbox = QSpinBox()
            self.sma_period_spinbox.setMinimum(1)
            self.sma_period_spinbox.setMaximum(200)
            self.sma_period_spinbox.setValue(10)
            self.rsi_label = QLabel("RSI: -")
            self.stoch_label = QLabel("Stoch: -")
            self.rsi_state_label = QLabel(self)
            self.rsi_status_label = QLabel(self)
            self.RSIDivergeRecommendation_label = QLabel(self)
            # Initialize the data fetcher and data processing objects
            self.data_fetcher = DataFetcher(EDGE_DRIVER_PATH)
            self.data_processing = DataProcessing(self)
            self.rsi_state_label = QLabel("RSI Status: -")
            self.RSIDivergeRecommendation_label = QLabel("RSI Divergance Detection: -")
            
            
            """Initialize the user interface layout."""
            main_layout = QHBoxLayout()

            # Create a QSplitter for horizontal splitting
            splitter = QSplitter()

            # 1. Left section: for ticker, buttons, and input boxes (10% of the screen)
            self.left_widget = QWidget()
            left_layout = QVBoxLayout()
            self.left_widget.setLayout(left_layout)
                    
            # Add the ticker label and input
            ticker_label = QLabel("Enter Ticker:")  # Adding a label for the ticker input
            left_layout.addWidget(ticker_label)
            left_layout.addWidget(self.ticker_input)
            
            left_layout.addWidget(self.rows_label)
            left_layout.addWidget(self.row_spin_box)
            left_layout.addWidget(self.sma_checkbox)
            left_layout.addWidget(self.rsi_checkbox)  # Adding the RSI checkbox
            left_layout.addWidget(self.stoch_checkbox)  # Adding the Stochastic Oscillator checkbox

            # Add the start and save buttons
            self.start_button = QPushButton("Start")
            try:
                self.start_button.clicked.connect(self.main_logic.start_fetching_data)
            except AttributeError as e:
                logging.error(f"AttributeError in setup_ui: {e}")
                raise
            left_layout.addWidget(self.start_button)

            self.save_button = QPushButton("Save")
            try:
                self.save_button.clicked.connect(self.main_logic.save_data_to_excel)
            except AttributeError as e:
                logging.error(f"AttributeError in setup_ui: {e}")
                raise
            left_layout.addWidget(self.save_button)
            
            splitter.addWidget(self.left_widget)  # Add to splitter

            # 2. Middle section: for the graph (80% of the screen)
            middle_widget = QWidget()
            middle_layout = QVBoxLayout()
            middle_widget.setLayout(middle_layout)
            self.setup_web_view(middle_layout)
            splitter.addWidget(middle_widget)

            # 3. Right section: for status (10% of the screen)
            self.right_widget = QWidget()
            right_layout = QVBoxLayout()
            self.right_widget.setLayout(right_layout)
                    
            # Add items to the right layout
            right_layout.addWidget(self.rsi_label)
            self.rsi_state_label.setToolTip("")

            right_layout.addWidget(self.rsi_state_label)  # Existing
            right_layout.addWidget(self.RSIDivergeRecommendation_label)  # New
            right_layout.addWidget(self.stoch_label)
            

            splitter.addWidget(self.right_widget)

            # Add the splitter to the main layout
            main_layout.addWidget(splitter)

            # Set the initial sizes (in pixels) according to the percentages given
            screen_width = self.width()  # Assuming this gives the width of the main window
            splitter.setSizes([int(0.05 * screen_width), int(0.80 * screen_width), int(0.15 * screen_width)])

            # Create a central widget with the main layout
            central_widget = QWidget()
            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)
            print("MainGUI: UI setup complete.")

        def connect_buttons(self):
            print("MainGUI: Connecting buttons...")
            """Connect signals of buttons to their corresponding slots."""
            self.sma_checkbox.stateChanged.connect(self.trigger_plot)
            self.rsi_checkbox.stateChanged.connect(self.trigger_plot)
            self.stoch_checkbox.stateChanged.connect(self.trigger_plot)
            self.sma_period_spinbox.valueChanged.connect(self.main_logic.recalculate_and_plot)
            print("MainGUI: Buttons connected.")

        def trigger_plot(self):
            print("MainGUI: Triggering plot...")
            if self.main_logic.df is not None:
                print("MainGUI: DataFrame is not None. Plotting chart.")
                self.data_processing.plot_candlestick_chart(self.main_logic.df)
            else:
                print("MainGUI: DataFrame is None. Skipping plot.")
                logging.warning("DataFrame not initialized. Skipping plot.")
            print("MainGUI: Plot triggered.")


        # ------- UI Component Setup Methods --------
    
        def setup_top_layout(self, main_layout):
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


        def setup_buttons_layout(self, main_layout):
            """Set up the layout for buttons."""
            buttons_layout = QHBoxLayout()

            start_button = QPushButton("Start")
            start_button.clicked.connect(self.start_fetching_data)
            buttons_layout.addWidget(start_button)

            save_button = QPushButton("Save")
            save_button.clicked.connect(self.save_data_to_excel)
            buttons_layout.addWidget(save_button)

            main_layout.addLayout(buttons_layout)

        def setup_web_view(self, main_layout):
            """Set up the web view for displaying charts."""
            self.web_view = QWebEngineView()
            print("Web view initialized.")
            main_layout.addWidget(self.web_view, 1)

        def setup_status_label(self, main_layout):
            """Set up the status label."""
            self.status_label = QLabel("Status: Ready")
            self.status_label.setFixedHeight(25)
            main_layout.addWidget(self.status_label)

        def setup_customize_button(self, main_layout):
            """Set up the "Customize Appearance" button."""
            customize_button = QPushButton("Customize Appearance")
            customize_button.clicked.connect(self.data_processing.update_chart_appearance)
            main_layout.addWidget(customize_button)
        # ------- Data Fetching and Processing Methods --------



   
class MainLogic:
        def __init__(self, gui_instance=None):
            print("MainLogic: Initializing...")
            logging.debug("MainLogic initialized.")
            self.gui = gui_instance
            print("MainLogic: Initialized.")
        def start_fetching_data(self):
            print("MainLogic: Starting data fetching...")
            logging.debug(f"GUI instance in start_fetching_data: {self.gui}")
            try:
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
                    # Calculate Stochastic Oscillator
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
                logging.error(f"AttributeError in start_fetching_data: {e}")
                self.gui.statusBar().showMessage("An error occurred. Check the log for details.")
            except ValueError as e:
                logging.error(f"ValueError in start_fetching_data: {e}")
                self.gui.statusBar().showMessage(str(e))
            except Exception as e:
                logging.error(f"An unexpected error occurred in start_fetching_data: {e}")
                self.gui.statusBar().showMessage("An unexpected error occurred. Check the log for details.")
            print("MainLogic: Data fetching complete.")  
        def update_gui_dataframe(self):
            self.gui.df = self.df
        def recalculate_and_plot(self):
            print("MainLogic: Recalculating and plotting...")
            try:
                if self.df is not None and not self.df.empty:
                    self.df = self.data_fetcher.calculate_sma(self.df.copy(), self.sma_period_spinbox.value()) # Recalculate SMA with the new period, using a copy to avoid side effects
                    self.update_gui_dataframe()
                    self.gui.data_processing.plot_candlestick_chart(self.df)  # Plot the updated chart
            except Exception as e:
                logging.error(f"An error occurred in recalculate_and_plot: {str(e)}")
                self.statusBar().showMessage("An error occurred. Check the log for details.")
            print("MainLogic: Data saved to Excel.")
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
                print("save_data_to_excel: Method invoked.")  # Entry point
                if self.df is not None:
                    print("save_data_to_excel: DataFrame is not None.")  # Check if DataFrame exists
                    
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
                    print("save_data_to_excel: Data successfully written to Excel.")  # Successful write to Excel
                    
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
        print("Main: Starting application...")
        app = QtWidgets.QApplication(sys.argv)

        # Initialize MainGUI and MainLogic
        logic = MainLogic()
        gui = MainGUI(main_logic=logic)

        # Link the two
        link_gui_and_logic(gui, logic)

        # Initialize the UI
        gui.initialize()

        gui.show()
        sys.exit(app.exec_())
        print("Main: Application started.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print("Main: An error occurred.")
        sys.exit(1)
