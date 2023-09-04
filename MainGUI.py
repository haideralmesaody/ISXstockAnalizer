# Standard Libraries
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from PyQt5.QtCore import pyqtSlot
# Third-party Libraries
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QSizePolicy,
                             QSpinBox, QSplitter, QTabWidget, QTextEdit, QVBoxLayout, QWidget)
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

# Local Imports
from app_config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE, DEBUG
)
from MainLogic import MainLogic
from LoggerFunction import Logger
from data_fetcher import DataFetcher
from data_visualizer import DataVisualizer
# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))


class MainGUI(QMainWindow):

    start_data_fetching_signal = pyqtSignal(str,int)
    save_data_signal = pyqtSignal()
    indicator_checkbox_changed_signal = pyqtSignal(list)
    indicator_values_updated_signal = pyqtSignal(dict)
    def __init__(self, data_processing=None):
        super(MainGUI, self).__init__()

        self.logger = Logger(DEBUG)  # Initialize the logger FIRST
        try:
            self.logger.log_or_print("MainGUI: Initializing...", level="DEBUG", module="MainGUI")

            self.data_processing = data_processing
            self.some_var = None  # Initialize all class variables here

            # Setup UI
            self.initialize_widgets()
            self.setup_ui()

            # Connect signals
            self.start_button.clicked.connect(self.emit_fetch_data_signal)
            self.save_button.clicked.connect(self.emit_save_data_signal)
            
            self.sma_checkbox.stateChanged.connect(self.on_indicator_checkbox_changed)
            self.rsi_checkbox.stateChanged.connect(self.on_indicator_checkbox_changed)
            self.rsi_9_checkbox.stateChanged.connect(self.on_indicator_checkbox_changed)
            self.rsi_25_checkbox.stateChanged.connect(self.on_indicator_checkbox_changed)
            self.stoch_checkbox.stateChanged.connect(self.on_indicator_checkbox_changed)
            #self.sma_checkbox.stateChanged.connect() - to be used later
            # ... (rest of your signal connections)

            self.logger.log_or_print("MainGUI: Initialized.", level="DEBUG", module="MainGUI")
            
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in MainGUI.__init__: {str(e)}. Stack Trace: {traceback.format_exc()}", level="ERROR", module="MainGUI")
            raise  # re-raise the exception for higher-level handling

    def initialize(self):
        self.logger.log_or_print("MainGUI: Initializing...", level="INFO", module="MainGUI")
        self.logger.log_or_print("MainGUI: About to initialize UI.", level="DEBUG", module="MainGUI")
        try:
            self.logger.log_or_print("About to call setup_ui...", level="DEBUG", module="MainGUI")
            #self.setup_ui()
            self.logger.log_or_print("Successfully called setup_ui.", level="DEBUG", module="MainGUI")
            self.logger.log_or_print("About to call connect_buttons...", level="DEBUG", module="MainGUI")
            self.connect_buttons()
            self.logger.log_or_print("Successfully called connect_buttons.", level="DEBUG", module="MainGUI")
            self.logger.log_or_print("MainGUI: UI Initialized.", level="INFO", module="MainGUI")
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in initialize: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
    # rest of your code...
            self.statusBar().showMessage("An unexpected error occurred. Check the log for details.")

    def setup_ui(self):
        self.logger.log_or_print("MainGUI: Creating UI...", level="INFO", module="MainGUI")
        self.logger.log_or_print("MainGUI: Starting UI setup.", level="DEBUG", module="MainGUI")
        try:
            # Initialize Widgets
            self.initialize_widgets()

            # Setup Layouts
            self.setup_layouts()

            # Assemble Final UI
            if not hasattr(self, 'splitter'):
                raise AttributeError("MainGUI object has no attribute 'splitter'")
            screen_width = self.width()
            self.splitter.setSizes([int(0.05 * screen_width), int(0.80 * screen_width), int(0.15 * screen_width)])

            self.logger.log_or_print("MainGUI: UI created successfully.", level="INFO", module="MainGUI")
            self.logger.log_or_print("MainGUI: Completed UI setup.", level="DEBUG", module="MainGUI")
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in create_ui: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
    # rest of your code...
            raise    


    def initialize_widgets(self):
        try:
            self.logger.log_or_print("MainGUI: Initializing RSI Details Tab widget.", level="DEBUG", module="MainGUI")
            self.rsi_details_tab = QTabWidget()
            self.rsi_interpretation_text = QTextEdit()
            self.rsi_divergence_text = QTextEdit()
            self.rsi_swing_text = QTextEdit()
            self.status_label = QLabel(self)
            self.ticker_input = QLineEdit()
            self.rows_label = QLabel("Number of rows:")
            self.row_spin_box = QSpinBox()
            self.row_spin_box.setMinimum(1)
            self.row_spin_box.setMaximum(1000)
            self.row_spin_box.setValue(300)
            self.sma_checkbox = QCheckBox("Show SMA")
            self.rsi_checkbox = QCheckBox("Show RSI_14")
            self.rsi_9_checkbox = QCheckBox("Show RSI_9")
            self.rsi_25_checkbox = QCheckBox("Show RSI_25")
            self.stoch_checkbox = QCheckBox("Show Stoch(9,6)")
            self.sma_period_spinbox = QSpinBox()
            self.sma_period_spinbox.setMinimum(1)
            self.sma_period_spinbox.setMaximum(200)
            self.sma_period_spinbox.setValue(10)
            self.rsi_9_label = QLabel("RSI_9: -")
            self.rsi_14_label = QLabel("RSI_14: -")
            self.rsi_25_label = QLabel("RSI_25: -")
            self.stoch_label = QLabel("Stoch: -")
            self.start_button = QPushButton("Start")
            self.save_button = QPushButton("Save")
            # Initialize Data Fetcher and Processor

            self.rsi_interpretation_text.setReadOnly(True)
            self.rsi_divergence_text.setReadOnly(True)
            self.rsi_swing_text.setReadOnly(True)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in initialize_widgets: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
    # rest of your code...
            raise
    def setup_layouts(self):
        try:
            self.logger.log_or_print("MainGUI: Setting up layouts.", level="DEBUG", module="MainGUI")
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
            left_layout.addWidget(self.rsi_9_checkbox)
            left_layout.addWidget(self.rsi_checkbox)
            left_layout.addWidget(self.rsi_25_checkbox)
            left_layout.addWidget(self.stoch_checkbox)
            left_layout.addWidget(self.start_button)               
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
            right_layout.addWidget(self.rsi_9_label)
            right_layout.addWidget(self.rsi_14_label)
            right_layout.addWidget(self.rsi_25_label)
            right_layout.addWidget(self.stoch_label)
            self.splitter.addWidget(self.right_widget)
            self.rsi_details_tab.addTab(self.rsi_interpretation_text, "RSI_Interpretation")
            self.rsi_details_tab.addTab(self.rsi_divergence_text, "RSI_Divergence")
            self.rsi_details_tab.addTab(self.rsi_swing_text, "RSI_Swing")
            right_layout.addWidget(self.rsi_details_tab)

            main_layout.addWidget(self.splitter)
            central_widget = QWidget()
            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in setup_layouts: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
    # rest of your code...
            raise
    def update_RSI_tabs(self):
        try:
            # Clear the tabs
            self.rsi_interpretation_text.clear()
            self.rsi_divergence_text.clear()
            self.rsi_swing_text.clear()

            # Ensure the dataframe is available
            if self.df is None or self.df.empty:
                raise ValueError("DataFrame is either None or empty. Cannot update RSI tabs.")

            # Get the last row of the dataframe which contains the latest data
            latest_data = self.df.iloc[-1]

            # Helper function to get RSI recommendation based on its value
            def get_rsi_recommendation(rsi_value):
                if rsi_value > 70:
                    return "Overbought: Asset might be overvalued. Consider potential selling opportunities."
                elif rsi_value < 30:
                    return "Oversold: Asset might be undervalued. Consider potential buying opportunities."
                else:
                    return "The asset is currently trading within a range. Monitor for breakout or breakdown from current levels."

            # Update RSI values and tabs for each RSI period
            for rsi_period in [9, 14, 25]:
                rsi_value = latest_data.get(f'RSI_{rsi_period}', None)
                if rsi_value:
                    # Update Interpretation Tab
                    self.rsi_interpretation_text.append(f"RSI {rsi_period}: {get_rsi_recommendation(rsi_value)}")

                    # Divergence Tab
                    bullish_divergence_flag = latest_data.get(f'RSI_{rsi_period}_Bullish Divergence_Flag', False)
                    bearish_divergence_flag = latest_data.get(f'RSI_{rsi_period}_Bearish Divergence_Flag', False)
                    if bullish_divergence_flag:
                        self.rsi_divergence_text.append(f"RSI {rsi_period}: Bullish Divergence detected. Might indicate a potential upward reversal.")
                    elif bearish_divergence_flag:
                        self.rsi_divergence_text.append(f"RSI {rsi_period}: Bearish Divergence detected. Might indicate a potential downward reversal.")
                    else:
                        self.rsi_divergence_text.append(f"RSI {rsi_period}: No divergence detected. The current price trend is confirmed by RSI. Continue monitoring for potential future divergences.")

                    # Swing Tab
                    swing_buy_flag = latest_data.get(f'RSI_{rsi_period}_Swing Failure Buy_Flag', False)
                    swing_sell_flag = latest_data.get(f'RSI_{rsi_period}_Swing Failure Sell_Flag', False)
                    if swing_buy_flag:
                        self.rsi_swing_text.append(f"RSI {rsi_period}: Swing Failure Buy detected. Might indicate a potential buy signal.")
                    elif swing_sell_flag:
                        self.rsi_swing_text.append(f"RSI {rsi_period}: Swing Failure Sell detected. Might indicate a potential sell signal.")
                    else:
                        self.rsi_swing_text.append(f"RSI {rsi_period}: No swing failures detected. The asset's momentum is consistent with its current trend. Stay alert for potential shifts in momentum in the future.")

                    # Update RSI Labels
                    label = getattr(self, f"rsi_{rsi_period}_label", None)
                    if label:
                        label.setText(f"RSI_{rsi_period}: {rsi_value:.2f}")

        except KeyError as ke:
            self.logger.log_or_print(f"KeyError while updating RSI tabs: {str(ke)}", level="ERROR", exc_info=True)
            self.statusBar().showMessage(f"KeyError: {str(ke)}")

        except ValueError as ve:
            self.logger.log_or_print(f"ValueError while updating RSI tabs: {str(ve)}", level="ERROR", exc_info=True)
            self.statusBar().showMessage(f"ValueError: {str(ve)}")

        except Exception as e:
            self.logger.log_or_print(f"Unexpected error while updating RSI tabs: {str(e)}", level="ERROR", exc_info=True)
            self.statusBar().showMessage(f"Unexpected error: {str(e)}")



    
    #def update_rsi_details(self):
    #    rsi_value = self.df['RSI_14'].iloc[-1]
    #    #rsi_status, rsi_description = self.gui.data_processing.interpret_rsi(rsi_value)
        #   self.gui.rsi_interpretation_text.setPlainText(f"RSI Value: {rsi_value}\nStatus: {rsi_status}\nDescription: {rsi_description}")

    def connect_buttons(self):
        try:
            self.logger.log_or_print("MainGUI: Connecting buttons...", level="DEBUG", module="MainGUI")

            # Connect start_button to its slot
            self.logger.log_or_print("MainGUI: Starting button-signal connections.", level="DEBUG", module="MainGUI")
            self.start_button.clicked.connect(self.emit_fetch_data_signal)

            # Connect save_button to its slot
            self.save_button.clicked.connect(self.emit_save_data_signal)

            # Connect checkboxes
            checkboxes = [
                self.sma_checkbox, self.rsi_checkbox, self.rsi_9_checkbox,
                self.rsi_25_checkbox, self.stoch_checkbox
            ]
            for checkbox in checkboxes:
                checkbox.stateChanged.connect(self.emit_plot_chart_signal)

            # Connect SpinBox
            self.sma_period_spinbox.valueChanged.connect(self.emit_recalculate_and_plot_signal)

            self.logger.log_or_print("MainGUI: Buttons connected.", level="DEBUG", module="MainGUI")
            self.logger.log_or_print("MainGUI: Completed button-signal connections.", level="DEBUG", module="MainGUI")
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in connect_buttons: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise


    def emit_fetch_data_signal(self):
        try:
            self.logger.log_or_print("emit_fetch_data_signal called", level="DEBUG", module="MainGUI")
            ticker = self.ticker_input.text().strip()
            if not ticker:
                raise ValueError("Ticker cannot be empty.")
            desired_rows = self.row_spin_box.value()
            self.start_data_fetching_signal.emit(ticker,desired_rows)
            self.logger.log_or_print("self.start_data_fetching_signal.emit(ticker, desired_rows) done", level="DEBUG", module="MainGUI")
        except ValueError as ve:
            self.on_data_fetch_error(str(ve), exc_info=True)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in emit_fetch_data_signal: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            self.on_data_fetch_error("An unexpected error occurred. Check the log for details.")
    def trigger_plot(self):
        try:
            self.logger.log_or_print("MainGUI: Triggering plot...", level="DEBUG", module="MainGUI")
            self.main_logic.plot_chart()  # Delegate to MainLogic
            self.logger.log_or_print("MainGUI: Plot triggered.", level="DEBUG", module="MainGUI")
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in trigger_plot: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
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
            self.rsi_checkbox = QCheckBox("Show RSI_14")
            top_layout.addWidget(self.rsi_checkbox)

            # Stochastic Oscillator Checkbox
            self.stoch_checkbox = QCheckBox("Show Stoch(9,6)")
            top_layout.addWidget(self.stoch_checkbox)

            main_layout.addLayout(top_layout)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in setup_top_layout: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
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
            self.logger.log_or_print(f"An unexpected error occurred in setup_buttons_layout: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise
    def setup_web_view(self, main_layout):
        try:
            """Set up the web view for displaying charts."""
            self.web_view = QWebEngineView()
            print("Web view initialized.")
            main_layout.addWidget(self.web_view, 1)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in setup_web_view: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise
    def setup_status_label(self, main_layout):
        try:
            """Set up the status label."""
            self.status_label = QLabel("Status: Ready")
            self.status_label.setFixedHeight(25)
            main_layout.addWidget(self.status_label)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in setup_status_label: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise
    def setup_customize_button(self, main_layout):
        try:
            """Set up the "Customize Appearance" button."""
            customize_button = QPushButton("Customize Appearance")
            customize_button.clicked.connect(self.data_processing.update_chart_appearance)
            main_layout.addWidget(customize_button)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in setup_customize_button: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise            
    # ------- Data Fetching and Processing Methods --------

    def on_data_fetched(self, dataframe):
        self.logger.log_or_print(f"on_data_fetched called.", level="DEBUG", module="MainGUI")
        try:
            """
            Slot to handle data fetched signal from MainLogic.
            Update the UI with the fetched data.
            """
            self.df = dataframe
            # You can add more UI updates based on the fetched data here
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in on_data_fetched: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise     
 
    def update_dataframe_slot(self, df):
        self.logger.log_or_print(f"update_dataframe_slot called.", level="DEBUG", module="MainGUI")
        try:
            
            self.df = df
            self.plot_chart_slot(df)
        except Exception as e:
            self.logger.log_or_print(f"An unexpected error occurred in update_dataframe_slot: {str(e)}", level="ERROR", module="MainGUI", exc_info=True)
            raise 
             

    def plot_chart(self):
                try:
                    if self.df is not None:  # Instead of checking the GUI's df directly, check the logic's df
                        self.logger.log_or_print("MainLogic: DataFrame is not None. Plotting chart.", level="DEBUG", module="MainLogic")
                        self.plotChartRequested.emit(self.df)
                    else:
                        self.logger.log_or_print("MainLogic: DataFrame is None. Skipping plot.", level="WARNING", module="MainLogic")
                except Exception as e:
                    self.logger.log_or_print(f"An unexpected error occurred in plot_chart: {str(e)}", level="ERROR", module="MainLogic")
                    raise            
    def enable_chart_interactions(self):
        try:
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
        except Exception as e:
            
            self.logger.log_or_print(f"An error occurred in enable_chart_interactions: {str(e)}", level="ERROR", module="MainLogic")

    def enable_data_point_highlight(self):
        try:
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
        except Exception as e:
            
            self.logger.log_or_print(f"An error occurred in enable_data_point_highlight: {str(e)}", level="ERROR", module="MainLogic")
    def update_chart(self, fig ):
        # Here, you'll use the data (df) to plot/update the chart in the GUI.
        # This might use some built-in Qt plotting or another library you have in mind.
        try:
            self.logger.log_or_print("Update_chart in MainGUI is called .", level="DEBUG", module="MainLogic")
            if fig is not None:
                raw_html = fig.to_html(include_plotlyjs='cdn')
            else:
                self.logger.log_or_print("fig is None, cannot convert to HTML", level="ERROR")
            self.web_view.setHtml(raw_html)
        except Exception as e:
            
            self.logger.log_or_print(f"An error occurred in update_chart: {str(e)}", level="ERROR", module="MainLogic")
    def emit_save_data_signal(self):
        try:
            self.logger.log_or_print("MainGUI: emit_save_data_signal triggered.", level="DEBUG", module="MainGUI")    
            self.save_data_signal.emit()
            self.logger.log_or_print("MainGUI: save_data_signal emitted.", level="DEBUG", module="MainGUI")

        except Exception as e:
            
            self.logger.log_or_print(f"An error occurred in emit_save_data_signal: {str(e)}", level="ERROR", module="MainLogic")
    def on_indicator_checkbox_changed(self):
        try:
            active_indicators = []

            if self.sma_checkbox.isChecked():
                active_indicators.append("SMA")
            if self.rsi_checkbox.isChecked():
                active_indicators.append("RSI_14")
            if self.rsi_9_checkbox.isChecked():
                active_indicators.append("RSI_9")
            if self.rsi_25_checkbox.isChecked():
                active_indicators.append("RSI_25")
            if self.stoch_checkbox.isChecked():
                active_indicators.append("STOCH")

            self.indicator_checkbox_changed_signal.emit(active_indicators)
        except Exception as e:
            
            self.logger.log_or_print(f"An error occurred in on_indicator_checkbox_changed: {str(e)}", level="ERROR", module="MainLogic")
    @pyqtSlot(dict)
    def update_indicator_labels(self, values):
        self.rsi_9_label.setText(f"RSI_9: {values.get('RSI_9', '-')}")
        self.rsi_14_label.setText(f"RSI_14: {values.get('RSI_14', '-')}")
        self.rsi_25_label.setText(f"RSI_25: {values.get('RSI_25', '-')}")
        if 'StochK' in values and 'StochD' in values:
            self.stoch_label.setText(f"Stoch(K): {values['StochK']:.2f}, Stoch(D): {values['StochD']:.2f}")