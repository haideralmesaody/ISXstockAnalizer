# Importing necessary libraries and modules
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
                             QLineEdit, QMainWindow, QPushButton, 
                             QSpinBox, QVBoxLayout, QWidget)
# Local Modules
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from data_fetcher import DataFetcher
from data_processing import DataProcessing
from PyQt5.QtCore import Qt
# Configure logging
from config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
# Set up logging with provided configurations

logging.basicConfig(**LOGGING_CONFIG)

# Get the current directory for potential file operations
current_directory = os.path.dirname(os.path.abspath(__file__))



class MainWindow(QMainWindow):
        """
        Main GUI window for the application.
        It integrates data fetching, processing, and visualization.
        """

        def __init__(self):
            super(MainWindow, self).__init__()
            # Initialize UI components and data handler objects
            self.initialize_ui_elements()
            self.data_fetcher = DataFetcher(EDGE_DRIVER_PATH)
            self.data_processing = DataProcessing(self)

            # Set up the UI layout
            self.setup_ui()

            # Connect button actions to their respective functions
            self.connect_buttons()

            # DataFrame to store the fetched stock data
            self.df = None
        def initialize_ui_elements(self):
            """Initialize the basic UI elements for the main window."""
            self.ticker_input = QLineEdit()
            self.ticker_input.setPlaceholderText("Enter ticker")
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
            self.sma_period_spinbox.setMaximum(100)
            self.sma_period_spinbox.setValue(10)
            self.rsi_label = QLabel("RSI: -")
            self.stoch_label = QLabel("Stoch: -")
            self.rsi_state_label = QLabel()

            # Initialize the data fetcher and data processing objects
            self.data_fetcher = DataFetcher(EDGE_DRIVER_PATH)
            self.data_processing = DataProcessing(self)

            # Initialize the user interface
            self.setup_ui()

            # Connect button signals to their respective slots
            self.connect_buttons()

            # Initialize DataFrame for data storage
            self.df = None

        def setup_ui(self):
            """Construct the main layout for the GUI."""
            main_layout = QHBoxLayout()

            # Create a QSplitter for horizontal splitting
            splitter = QSplitter()
            # UI sections setup
            self.setup_left_section(splitter)
            self.setup_middle_section(splitter)
            self.setup_right_section(splitter)    

            # Add the splitter to the main layout
            main_layout.addWidget(splitter)

            # Set the initial sizes (in pixels) according to the percentages given
            screen_width = self.width()  # Assuming this gives the width of the main window
            splitter.setSizes([int(0.10 * screen_width), int(0.80 * screen_width), int(0.10 * screen_width)])

            # Create a central widget with the main layout
            central_widget = QWidget()
            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)
        def setup_left_section(self, splitter):
            """Construct the left section of the UI."""
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
            left_layout.addWidget(self.start_button)

            self.save_button = QPushButton("Save")
            left_layout.addWidget(self.save_button)
            
            splitter.addWidget(self.left_widget)  # Add to splitter
        def setup_middle_section(self, splitter):
            """Construct the middle section for displaying the graph."""
            # 2. Middle section: for the graph (80% of the screen)
            middle_widget = QWidget()
            middle_layout = QVBoxLayout()
            middle_widget.setLayout(middle_layout)
            self.setup_web_view(middle_layout)
            splitter.addWidget(middle_widget)
        def setup_right_section(self, splitter):
            """Construct the right section for displaying status info."""
            # 3. Right section: for status (10% of the screen)
            self.right_widget = QWidget()
            self.right_layout = QVBoxLayout() 
            self.right_widget.setLayout(self.right_layout)
                    
            # Add items to the right layout
            self.right_layout.addWidget(self.rsi_label)
            self.rsi_state_label.setToolTip("")
            right_layout.addWidget(self.stoch_label)
            self.rsi_state_label = QLabel()
            right_layout.addWidget(self.rsi_state_label)  # Add to right layout directly
            
            splitter.addWidget(self.right_widget)
        def connect_buttons(self):
            """Connect signals of buttons to their corresponding slots."""
            self.sma_checkbox.stateChanged.connect(self.data_processing.plot_candlestick_chart)
            self.sma_period_spinbox.valueChanged.connect(self.recalculate_and_plot)
            self.rsi_checkbox.stateChanged.connect(self.data_processing.plot_candlestick_chart)
            self.stoch_checkbox.stateChanged.connect(self.data_processing.plot_candlestick_chart)
            self.start_button.clicked.connect(self.start_fetching_data)
            self.save_button.clicked.connect(self.save_data_to_excel)

        # ------- UI Component Setup Methods --------
    
        def setup_top_layout(self, main_layout):
            """Set up the top layout containing input widgets."""
            top_layout = QHBoxLayout()

            top_layout.addWidget(self.ticker_input)

            self.rows_label = QLabel("Number of rows:")
            top_layout.addWidget(self.rows_label)


            top_layout.addWidget(self.row_spin_box)

            self.sma_checkbox = QCheckBox("Show SMA")
            top_layout.addWidget(self.sma_checkbox)

            self.sma_period_label = QLabel("SMA Period:")
            top_layout.addWidget(self.sma_period_label)
            

            top_layout.addWidget(self.sma_period_spinbox)

            # RSI Checkbox
            self.rsi_checkbox = QCheckBox("Show RSI14")
            top_layout.addWidget(self.rsi_checkbox)

            # Stochastic Oscillator Checkbox

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


        def start_fetching_data(self):
            print("About to plot the candlestick chart...")
            """Fetch and process data based on user input."""
            try:
                ticker = self.ticker_input.text().strip()
                desired_rows = self.row_spin_box.value()
                if ticker:
                    logging.info(f"Processing ticker: {ticker}...")
                    self.df = self.data_fetcher.fetch_data(ticker, desired_rows)
                    # Calculate Stochastic Oscillator
                    self.df = self.data_fetcher.calculate_stochastic_oscillator(self.df)
                    # After calculating Stochastic Oscillator and before plotting
                    self.df['%K'] = self.df['%K'].clip(lower=0, upper=100)
                    self.df['%D'] = self.df['%D'].clip(lower=0, upper=100)
                    self.data_processing.plot_candlestick_chart()
                    print(self.df.columns)
                print("NaN values in df:", self.df.isna().sum())
                print("Columns in the DataFrame in MainWindow after data fetching:")
                print(self.df.columns)
                # Get the last date's RSI value and interpret its status
                rsi_value = self.df['RSI14'].iloc[-1]
                rsi_status, rsi_description = self.data_processing.interpret_rsi(rsi_value)
                # Update the status label in the UI
                self.rsi_status_label.setText(f"RSI ({rsi_value:.2f}): {rsi_status}")
                self.rsi_status_label.setToolTip(rsi_description)
            except Exception as e:
                logging.error(f"An error occurred in start_fetching_data: {str(e)}")
                self.statusBar().showMessage("An error occurred. Check the log for details.")

        

        

        def recalculate_and_plot(self):
            try:
                if self.df is not None and not self.df.empty:
                    self.df = self.data_fetcher.calculate_sma(self.df.copy(), self.sma_period_spinbox.value()) # Recalculate SMA with the new period, using a copy to avoid side effects
                    self.data_processing.plot_candlestick_chart()  # Plot the updated chart
            except Exception as e:
                logging.error(f"An error occurred in recalculate_and_plot: {str(e)}")
                self.statusBar().showMessage("An error occurred. Check the log for details.")

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
            print(self.df.columns)
            try:
                if self.df is not None:
                    # Get the current datetime
                    now = datetime.now()
                    # Format the datetime and combine with the ticker name to form the filename
                    ticker = self.ticker_input.text().strip()
                    filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}.xlsx"
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        self.df.to_excel(writer, sheet_name='Sheet1', index=False) # This already includes all columns, including RSI14
                        print("Saving Stoch data to Excel...")
                        stoch_df = self.df[['Date', '%K', '%D']]
                        print("First few rows of Stoch data to be saved:")
                        print(stoch_df.head())
                        self.df[['Date', 'High', 'Low', 'Close']].to_excel(writer, sheet_name='Sheet2', index=False)
                        self.df[['Date', 'Volume', 'High', 'Low', 'Close']].to_excel(writer, sheet_name='Sheet3', index=False)
                        self.df[['Volume', 'Open', 'High', 'Low', 'Close']].to_excel(writer, sheet_name='Sheet4', index=False)
                        sma_df = self.df[['Date', 'High', 'Low', 'Close','SMA','SMA50', 'SMA200']]
                        sma_df.to_excel(writer, sheet_name='SMA', index=False)
                        stoch_df = self.df[['Date', '%K', '%D']] # Assuming Stoch_K and Stoch_D as column names for Stochastic Oscillator
                        stoch_df.to_excel(writer, sheet_name='Stoch(9,6)', index=False)
                    self.status_label.setText("Data saved successfully.")
                else:
                    self.status_label.setText("No data available to save.")
            except Exception as e:
                logging.error(f"An error occurred in save_data_to_excel: {str(e)}") 
                self.statusBar().showMessage("An error occurred. Check the log for details.")
   



        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
