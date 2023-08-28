# data_processing.py

import plotly.express as px
import plotly.graph_objects as go
import logging
class DataProcessing:
    def __init__(self, main_window):
        self.main_window = main_window

    def plot_candlestick_chart(self):
        print("In plot_candlestick_chart method...")
        try:
            # Basic candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=self.main_window.df['Date'],
                                                open=self.main_window.df['Open'],
                                                high=self.main_window.df['High'],
                                                low=self.main_window.df['Low'],
                                                close=self.main_window.df['Close'])])
            self.main_window.df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
            if self.main_window.sma_checkbox.isChecked():
                if 'SMA' in self.main_window.df.columns:
                    fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['SMA'], mode='lines', name='SMA'))
                if 'SMA50' in self.main_window.df.columns:
                    fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['SMA50'], mode='lines', name='SMA50'))
                if 'SMA200' in self.main_window.df.columns:
                    fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['SMA200'], mode='lines', name='SMA200'))
            # Add RSI
            if self.main_window.rsi_checkbox.isChecked() and 'RSI14' in self.main_window.df.columns:
                    # Change the color of the RSI trace (e.g., to "blue")
                fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['RSI14'], mode='lines', name='RSI14', yaxis='y2', line=dict(color='blue')))
                
                # Add guidelines at 70 and 30 for RSI
                fig.add_shape(type="line",
                            x0=self.main_window.df['Date'].iloc[0], x1=self.main_window.df['Date'].iloc[-1],
                            y0=70, y1=70,
                            yref='y2',
                            line=dict(color="blue", width=2)) # Change the color (e.g., to "green")
                fig.add_shape(type="line",
                            x0=self.main_window.df['Date'].iloc[0], x1=self.main_window.df['Date'].iloc[-1],
                            y0=30, y1=30,
                            yref='y2',
                            line=dict(color="blue", width=2))  # Change the color (e.g., to "red")
                # Add Stochastics
            if self.main_window.stoch_checkbox.isChecked() and '%K' in self.main_window.df.columns and '%D' in self.main_window.df.columns:
                fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['%K'], mode='lines', name='%K', yaxis='y2'))
                fig.add_trace(go.Scatter(x=self.main_window.df['Date'], y=self.main_window.df['%D'], mode='lines', name='%D', yaxis='y2'))
                # Add guidelines at 20 and 80 for Stochastic Oscillator
                fig.add_shape(type="line",
                            x0=self.main_window.df['Date'].iloc[0], x1=self.main_window.df['Date'].iloc[-1],
                            y0=20, y1=20,
                            yref='y2',
                            line=dict(color="blue", width=2))
                fig.add_shape(type="line",
                            x0=self.main_window.df['Date'].iloc[0], x1=self.main_window.df['Date'].iloc[-1],
                            y0=80, y1=80,
                            yref='y2',
                            line=dict(color="blue", width=2))
            y2_data = []
            if 'RSI14' in self.main_window.df.columns:
                y2_data.extend(self.main_window.df['RSI14'].tolist())
            if '%K' in self.main_window.df.columns:
                y2_data.extend(self.main_window.df['%K'].tolist())
            if '%D' in self.main_window.df.columns:
                y2_data.extend(self.main_window.df['%D'].tolist())
                
            if y2_data:
                y2_min = min(y2_data) - 5  # Adjusted to capture values slightly below 0
                y2_max = max(y2_data) + 5  # Adjusted to capture values slightly above 100
                fig.update_layout(
                    yaxis2=dict(title="Indicators", overlaying='y', side='right', range=[y2_min, y2_max])
                )
            # Convert to HTML and update the web view
            raw_html = fig.to_html(include_plotlyjs='cdn')
            self.main_window.web_view.setHtml(raw_html)
            self.main_window.web_view.update()
            # After plotting the chart, update the labels with the latest values
            # After plotting the chart, update the labels with the latest values
            latest_row = self.main_window.df.iloc[-1]  # Get the last row of the dataframe

            latest_rsi = latest_row['RSI14']  # Fetch the RSI14 value from the last row
            if '%K' in self.main_window.df.columns and '%D' in self.main_window.df.columns:
                latest_stoch_k = latest_row['%K']
                latest_stoch_d = latest_row['%D']

            self.main_window.rsi_label.setText(f"RSI: {latest_rsi:.2f}")
            self.main_window.stoch_label.setText(f"Stoch K: {latest_stoch_k:.2f}, D: {latest_stoch_d:.2f}")
            if 'RSI14' in self.main_window.df.columns:
                latest_rsi = latest_row['RSI14']
            print("Calling RSI interpreter")
            state, description = self.interpret_rsi(latest_rsi)
            self.main_window.rsi_state_label.setText(f"RSI State: {state}")
            self.main_window.rsi_state_label.setToolTip(description)
        except Exception as e:
            logging.error(f"An error occurred in plot_candlestick_chart: ")

    def update_chart_appearance(self):
            """Update the appearance of the chart."""
            try:
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
                print("Graph should be updated now.")
            except Exception as e:
                logging.error(f"An error occurred in update_chart_appearance: {str(e)}")
    def interpret_rsi(self, rsi_value):
        print("RSI Interpreter is called")
        if rsi_value < 30:
            state = "Oversold"
            description = "The asset might be undervalued and is a potential buying opportunity."
        elif rsi_value > 70:
            state = "Overbought"
            description = "The asset might be overvalued and is a potential selling opportunity."
        else:
            state = "Neutral"
            description = "The asset is neither overbought nor oversold. It's in a neutral state."
        print(f"the state of the RSI is {state}")
        return state, description
    # ... Add all other data processing and visualization methods ...
