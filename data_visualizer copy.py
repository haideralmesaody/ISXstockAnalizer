import plotly.express as px
import plotly.graph_objects as go
from LoggerFunction import Logger  # Import your Logger class
from PyQt5.QtCore import pyqtSignal, QObject

class DataVisualizer(QObject):
    """
    A class to visualize stock market data using candlestick charts and various indicators.
    """
    
    chart_ready_signal = pyqtSignal(object)  # Emitted when the chart is ready
    
    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def plot_candlestick_chart(self, df=None, indicators=None):
        """
        Generates a candlestick chart from the provided dataframe.

        Parameters:
        - df: pandas DataFrame containing stock data
        - indicators: list of indicators to be plotted on the chart

        Emits:
        - chart_ready_signal: emits the generated figure for rendering
        """
        try:
            self.logger.log_or_print("plot_candlestick_chart: Function called. Attempting to process DataFrame...", level='DEBUG')
            
            if df is None:
                raise ValueError("No DataFrame provided for plotting.")
                
            self.logger.log_or_print("plot_candlestick_chart: DataFrame is available.", level='DEBUG')
            
            # Initialize the layout with secondary y-axis settings
            layout = go.Layout(
                yaxis=dict(domain=[0, 0.8]),
                yaxis2=dict(domain=[0.8, 1], overlaying='y', side='right')
            )
            
            # Create an empty Figure with the layout
            fig = go.Figure(layout=layout)
            
            # Add the candlestick trace to the primary y-axis
            fig.add_trace(go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close']))
            
            df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
            
            # Check for indicators and plot accordingly
            if indicators:
                if 'SMA' in indicators:
                    for sma_col in ['SMA', 'SMA50', 'SMA200']:
                        if sma_col in df.columns:
                            fig.add_trace(go.Scatter(x=df['Date'], y=df[sma_col], mode='lines', name=sma_col))
                            
                if 'RSI_14' in indicators and 'RSI_14' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_14'], mode='lines', name='RSI_14', yaxis='y2', line=dict(color="orange", width=2)))
                    # Guidelines for RSI
                    self._add_rsi_guidelines_to_fig(fig, df)
                
                if 'RSI_25' in indicators and 'RSI_25' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_25'], mode='lines', name='RSI_25', yaxis='y2', line=dict(color="orange", width=2)))
                    # Guidelines for RSI
                    self._add_rsi_guidelines_to_fig(fig, df)
                
                if 'RSI_9' in indicators and 'RSI_9' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_9'], mode='lines', name='RSI_9', yaxis='y2', line=dict(color="orange", width=2)))
                    # Guidelines for RSI
                    self._add_rsi_guidelines_to_fig(fig, df)
                
                if 'STOCH' in indicators and 'STOCHk_9_6_3' in df.columns and 'STOCHd_9_6_3' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['STOCHk_9_6_3'], mode='lines', name='STOCHk_9_6_3', yaxis='y2', line=dict(color="orange", width=2)))
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['STOCHd_9_6_3'], mode='lines', name='STOCHd_9_6_3', yaxis='y2', line=dict(color="Black", width=2)))
                    # Guidelines for Stochastic Oscillator
                    self._add_stoch_guidelines_to_fig(fig, df)
                if 'CMF_20' in indicators and 'CMF_20' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['CMF_20'], mode='lines', name='CMF_20', yaxis='y2', line=dict(color="orange", width=2)))
                if 'MACD_12_26_9' in indicators and 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD_12_26_9'], mode='lines', name='STOCHk_9_6_3', yaxis='y2', line=dict(color="orange", width=2)))
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACDs_12_26_9'], mode='lines', name='STOCHd_9_6_3', yaxis='y2', line=dict(color="Black", width=2)))
                    # Guidelines for Stochastic Oscillator
            
            self.logger.log_or_print("plot_candlestick_chart: DataFrame processed. Returning the processed figure.", level='DEBUG')
            self.chart_ready_signal.emit(fig)
        except ValueError as ve:
            self.logger.log_or_print(f"plot_candlestick_chart: ValueError encountered: {ve}", level='ERROR', exc_info=True)
        except KeyError as ke:
            self.logger.log_or_print(f"plot_candlestick_chart: KeyError encountered: {ke}", level='ERROR', exc_info=True)
        except Exception as e:
            self.logger.log_or_print(f"plot_candlestick_chart: Unexpected error encountered: {e}", level='ERROR', exc_info=True)

    def _add_rsi_guidelines_to_fig(self, fig, df):
        """
        Add RSI (Relative Strength Index) guidelines to the chart figure.

        Parameters:
        - fig: the Figure object to which RSI guidelines are added
        - df: pandas DataFrame used to determine the range of x-axis
        """
        # Add guidelines at 70 and 30 for RSI
        fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=70, y1=70, yref='y2', line=dict(color="blue", width=2))
        fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=30, y1=30, yref='y2', line=dict(color="blue", width=2))
        
    def _add_stoch_guidelines_to_fig(self, fig, df):
        """
        Add Stochastic Oscillator guidelines to the chart figure.

        Parameters:
        - fig: the Figure object to which the guidelines are added
        - df: pandas DataFrame used to determine the range of x-axis
        """
        # Guidelines for Stochastic Oscillator
        fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=20, y1=20, yref='y2', line=dict(color="blue", width=2))
        fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=80, y1=80, yref='y2', line=dict(color="blue", width=2))
