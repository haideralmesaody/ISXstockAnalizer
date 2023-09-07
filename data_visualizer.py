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
        try:
            self.logger.log_or_print("plot_candlestick_chart: Function called. Attempting to process DataFrame...", level='DEBUG')
            
            if df is None:
                raise ValueError("No DataFrame provided for plotting.")
                
            self.logger.log_or_print("plot_candlestick_chart: DataFrame is available.", level='DEBUG')

            # Colors
            primary_color = "#2E86C1"  # Blueish for primary traces like candlesticks
            sma_colors = {
                'SMA': "#A569BD",  # Purple for SMA
                'SMA50': "#3498DB",  # Light blue for SMA50
                'SMA200': "#F4D03F"  # Yellow for SMA200
            }
            secondary_color = "#C0392B"  # Redish for secondary indicators
            tertiary_color = "#196F3D"  # Greenish for tertiary indicators
            quaternary_color = "#8c564b"  # Brownish for other indicators
            quinary_color = "#e377c2"  # Pinkish for further indicators

            # Initialize the layout with secondary y-axis settings
            layout = go.Layout(
                yaxis=dict(domain=[0, 0.8]),
                yaxis2=dict(domain=[0.8, 1], overlaying='y', side='right')
            )
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Candlestick(x=df['Date'],
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close']))

            df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)

            if indicators:
                # For SMA traces
                if 'SMA' in indicators:
                    for sma_col in ['SMA', 'SMA50', 'SMA200']:
                        if sma_col in df.columns:
                            fig.add_trace(go.Scatter(x=df['Date'], y=df[sma_col], mode='lines', name=sma_col, line=dict(color=sma_colors[sma_col], width=2.5)))
                            self.annotate_sma_events(fig,df)
                
                # RSI_14
                if 'RSI_14' in indicators and 'RSI_14' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_14'], mode='lines', name='RSI_14', yaxis='y2', line=dict(color=secondary_color, width=2.5)))
                    self._add_rsi_guidelines_to_fig(fig, df)

                # RSI_25
                if 'RSI_25' in indicators and 'RSI_25' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_25'], mode='lines', name='RSI_25', yaxis='y2', line=dict(color=tertiary_color, width=2.5)))
                    self._add_rsi_guidelines_to_fig(fig, df)

                # RSI_9
                if 'RSI_9' in indicators and 'RSI_9' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_9'], mode='lines', name='RSI_9', yaxis='y2', line=dict(color=quaternary_color, width=2.5)))
                    self._add_rsi_guidelines_to_fig(fig, df)
                    
                # Stochastic Oscillator
                if 'STOCH' in indicators:
                    if 'STOCHk_9_6_3' in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df['STOCHk_9_6_3'], mode='lines', name='STOCHk_9_6_3', yaxis='y2', line=dict(color=secondary_color, width=2.5)))
                    if 'STOCHd_9_6_3' in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df['STOCHd_9_6_3'], mode='lines', name='STOCHd_9_6_3', yaxis='y2', line=dict(color=tertiary_color, width=2.5)))
                    self._add_stoch_guidelines_to_fig(fig, df)

                # Chaikin Money Flow
                if 'CMF_20' in indicators and 'CMF_20' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['CMF_20'], mode='lines', name='CMF_20', yaxis='y2', line=dict(color=quaternary_color, width=2.5)))

                # MACD
                if 'MACD_12_26_9' in indicators:
                    if 'MACD_12_26_9' in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD_12_26_9'], mode='lines', name='MACD_12_26_9', yaxis='y2', line=dict(color=secondary_color, width=2.5)))
                    if 'MACDs_12_26_9' in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df['MACDs_12_26_9'], mode='lines', name='MACDs_12_26_9', yaxis='y2', line=dict(color=tertiary_color, width=2.5)))
                    if 'MACDh_12_26_9' in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df['MACDh_12_26_9'], mode='lines', name='MACDh_12_26_9', yaxis='y2', line=dict(color=quinary_color, width=2.5)))
            
            fig.update_layout(
                hovermode="x unified",
                title="Stock Market Data",
                xaxis_title="Date",
                yaxis_title="Stock Price",
                yaxis2_title="Indicator Value",
                font=dict(
                    family="Courier New, monospace",
                    size=12,
                    color=primary_color
                ),
                plot_bgcolor="#FAFAFA",  # Light gray background color for better visibility
                paper_bgcolor="#FAFAFA"  # Matching paper color
            )
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


    def annotate_sma_events(self, fig, df):
        """
        Annotate significant SMA related events on the chart figure.
        """
        try:


            for i, row in df.iterrows():
                x_val = row['Date']

                # Annotating Golden Cross
                if row['Golden_Cross']:
                    fig.add_annotation(
                        x=row['Date'],
                        y=row['Close'],
                        text="Golden Cross",
                        showarrow=True,
                        arrowhead=4,
                        ax=0,
                        ay=-40,
                        bgcolor="#FFEB3B",  # Yellow for Golden Cross
                        opacity=0.8
                    )

                # Annotating Death Cross
                if row['Death_Cross']:
                    fig.add_annotation(
                        x=row['Date'],
                        y=row['Close'],
                        text="Death Cross",
                        showarrow=True,
                        arrowhead=4,
                        ax=0,
                        ay=40,
                        bgcolor="#FF5722",  # Red for Death Cross
                        opacity=0.8
                    )

                # Price crossing SMA50 and SMA200
                if row['Price_Cross_SMA50_Up'] == 1:
                    fig.add_annotation(x=x_val, y=row['Close'], text="Price crosses SMA50 Up", showarrow=True, arrowhead=2)
                elif row['Price_Cross_SMA50_Down'] == 1:
                    fig.add_annotation(x=x_val, y=row['Close'], text="Price crosses SMA50 Down", showarrow=True, arrowhead=2)

                if row['Price_Cross_SMA200_Up'] == 1:
                    fig.add_annotation(x=x_val, y=row['Close'], text="Price crosses SMA200 Up", showarrow=True, arrowhead=2)
                elif row['Price_Cross_SMA200_Down'] == 1:
                    fig.add_annotation(x=x_val, y=row['Close'], text="Price crosses SMA200 Down", showarrow=True, arrowhead=2)

            fig.update_annotations(dict(
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40
            ))
            self.logger.log_or_print("annotate_sma_events: Successfully annotated significant SMA related events.", level='DEBUG')

        except KeyError as ke:
            self.logger.log_or_print(f"annotate_sma_events: KeyError encountered: {ke}", level='ERROR', exc_info=True)
        except Exception as e:
            self.logger.log_or_print(f"annotate_sma_events: Unexpected error encountered: {e}", level='ERROR', exc_info=True)
