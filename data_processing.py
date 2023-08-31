# data_processing.py

import plotly.express as px
import plotly.graph_objects as go
import logging
from LoggerFunction import Logger  # Import your Logger class
class DataProcessing:
    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = Logger()

    def plot_candlestick_chart(self, df=None):
        try:
            self.logger.log_or_print("plot_candlestick_chart: Function called. Attempting to process DataFrame...", level='DEBUG')
            
            if df is None:
                raise ValueError("No DataFrame provided for plotting.")
                

            self.logger.log_or_print("plot_candlestick_chart: DataFrame is available.", level='DEBUG')
            
            # Initialize the layout with secondary y-axis settings
            layout = go.Layout(
                yaxis=dict(domain=[0, 0.8]),  # primary y-axis (y) occupies 80% from the bottom
                yaxis2=dict(domain=[0.8, 1], overlaying='y', side='right')  # secondary y-axis (y2) occupies top 20%, overlaying y
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
            
            # SMA Checkbox Checked
            if self.main_window.sma_checkbox.isChecked():
                self.logger.log_or_print("plot_candlestick_chart: SMA Checkbox is checked.", level='DEBUG')
                for sma_col in ['SMA', 'SMA50', 'SMA200']:
                    if sma_col in df.columns:
                        fig.add_trace(go.Scatter(x=df['Date'], y=df[sma_col], mode='lines', name=sma_col))
            
            # RSI Checkbox Checked
            if self.main_window.rsi_checkbox.isChecked() and 'RSI14' in df.columns:
                self.logger.log_or_print("plot_candlestick_chart: RSI Checkbox is checked.", level='DEBUG')
                fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI14'], mode='lines', name='RSI14', yaxis='y2', line=dict(color="orange", width=2)))
                
                # Add guidelines at 70 and 30 for RSI
                fig.add_shape(type="line",
                              x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1],
                              y0=70, y1=70,
                              yref='y2',
                              line=dict(color="blue", width=2))
                
                fig.add_shape(type="line",
                              x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1],
                              y0=30, y1=30,
                              yref='y2',
                              line=dict(color="blue", width=2))
            
            # Stochastic Oscillator Checkbox Checked
            if self.main_window.stoch_checkbox.isChecked() and '%K' in df.columns and '%D' in df.columns:
                self.logger.log_or_print("plot_candlestick_chart: Stoch Checkbox is checked.", level='DEBUG')
                fig.add_trace(go.Scatter(x=df['Date'], y=df['%K'], mode='lines', name='%K', yaxis='y2', line=dict(color="orange", width=2)))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['%D'], mode='lines', name='%D', yaxis='y2', line=dict(color="Black", width=2)))
                
                # Add guidelines at 20 and 80 for Stochastic Oscillator
                fig.add_shape(type="line",
                              x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1],
                              y0=20, y1=20,
                              yref='y2',
                              line=dict(color="blue", width=2))
                
                fig.add_shape(type="line",
                              x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1],
                              y0=80, y1=80,
                              yref='y2',
                              line=dict(color="blue", width=2))
            self.logger.log_or_print("plot_candlestick_chart: DataFrame processed. Attempting to update the web view...", level='DEBUG')
            # Update the web view
            raw_html = fig.to_html(include_plotlyjs='cdn')
            self.main_window.web_view.setHtml(raw_html)
            self.logger.log_or_print("plot_candlestick_chart: Web view updated successfully.", level='DEBUG')
            # Update the labels
            latest_row = df.iloc[-1]
            self.main_window.rsi_label.setText(f"RSI: {latest_row['RSI14']:.2f}")
            self.main_window.stoch_label.setText(f"Stoch K: {latest_row['%K']:.2f}, D: {latest_row['%D']:.2f}")
            print("plot_candlestick_chart: Function execution complete.")
        except ValueError as ve:
            self.logger.log_or_print(f"plot_candlestick_chart: ValueError encountered: {ve}", level='ERROR', exc_info=True)
            self.main_window.statusBar().showMessage(str(ve))
        except KeyError as ke:
            self.logger.log_or_print(f"plot_candlestick_chart: KeyError encountered:: {ve}", level='ERROR', exc_info=True)
            self.main_window.statusBar().showMessage(f"Missing key in DataFrame: {ke}")
        except Exception as e:
            self.logger.log_or_print(f"plot_candlestick_chart: Unexpected error encountered: {ve}", level='ERROR', exc_info=True)

            self.main_window.statusBar().showMessage("An unexpected error occurred. Check the log for details.")
    def update_chart_appearance(self):
            """Update the appearance of the chart."""
            try:
                self.logger.log_or_print("update_chart_appearance: Function called. Attempting to update chart appearance...", level='DEBUG')
                fig = go.Figure(data=[go.Candlestick(x=self.main_window.df['Date'],
                                                    open=self.main_window.df['Open'],
                                                    high=self.main_window.df['High'],
                                                    low=self.main_window.df['Low'],
                                                    close=self.main_window.df['Close'])])

                # Apply custom appearance settings
                fig.update_layout(
                    title="Custom Candlestick Chart",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    yaxis=dict(autorange=True, fixedrange=False),  # Allow y-axis zooming
                    colorway=["green", "red"],  # Change color scheme
                )

                raw_html = fig.to_html(include_plotlyjs='cdn')
                self.main_window.web_view.setHtml(raw_html)
                self.logger.log_or_print("update_chart_appearance: Chart appearance updated successfully.", level='DEBUG')
            except Exception as e:
                self.logger.log_or_print(f"An error occurred in update_chart_appearance: {3}", level='ERROR', exc_info=True)

    def interpret_rsi(self, rsi_value):
        try:
            self.logger.log_or_print("RSI Interpreter is called", level='DEBUG')
            if rsi_value < 30:
                state = "Oversold"
                description = "The asset might be undervalued and is a potential buying opportunity."
            elif rsi_value > 70:
                state = "Overbought"
                description = "The asset might be overvalued and is a potential selling opportunity."
            else:
                state = "Neutral"
                description = "The asset is neither overbought nor oversold. It's in a neutral state."
            self.logger.log_or_print(f"the state of the RSI is {state}", level='DEBUG')
            return state, description
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in ... {str(e)}", level='ERROR', exc_info=True)
    # ... Add all other data processing and visualization methods ...
    def detect_divergences(self, df):
        try:
            self.logger.log_or_print("detect_divergences: Function called. Processing DataFrame...", level='DEBUG')
            # Find local lows for price and RSI
            price_low = df['Close'].rolling(window=5).apply(lambda x: x.idxmin())
            rsi_low = df['RSI14'].rolling(window=5).apply(lambda x: x.idxmin())

            # Find local highs for price and RSI
            price_high = df['Close'].rolling(window=5).apply(lambda x: x.idxmax())
            rsi_high = df['RSI14'].rolling(window=5).apply(lambda x: x.idxmax())
            
            bullish_divergence = (price_low.diff() < 0) & (rsi_low.diff() > 0)
            bearish_divergence = (price_high.diff() > 0) & (rsi_high.diff() < 0)

            df['Bullish Divergence'] = bullish_divergence
            df['Bearish Divergence'] = bearish_divergence
            self.logger.log_or_print("detect_divergences: DataFrame processed successfully.", level='DEBUG')
            return df
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in detect_divergences: {str(e)}", level='ERROR', exc_info=True)
            return df
    def provide_recommendation(self):
        try:
            self.logger.log_or_print("provide_recommendation: Function called. Providing recommendation...", level='DEBUG')
            last_row = self.main_window.df.iloc[-1]  # Fetch the last row of the dataframe
            if last_row['Bullish Divergence']:
                return "Bullish divergence detected. Consider potential buying opportunities."
            elif last_row['Bearish Divergence']:
                return "Bearish divergence detected. Consider potential selling opportunities."
            else:
                return "No clear divergence detected. Monitor the market for other signals."
            self.logger.log_or_print("provide_recommendation: Recommendation provided successfully.", level='DEBUG')
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in provide_recommendation: {str(e)}", level='ERROR', exc_info=True)