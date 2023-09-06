import logging
import time
from datetime import datetime
import pandas as pd
import pandas_ta as ta
from bs4 import BeautifulSoup
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from app_config import (
    LOGGING_CONFIG, EDGE_DRIVER_PATH, BASE_URL, DEFAULT_DATE,
    TABLE_SELECTOR, WEBDRIVER_WAIT_TIME, DEFAULT_SMA_PERIOD,
    DEFAULT_ROW_COUNT, EXCEL_ENGINE
)
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from LoggerFunction import Logger  # Import your Logger class
class DataCalculator(QObject):
    # Define signals for each calculation method
    sma_calculated_signal = pyqtSignal(pd.DataFrame)
    rsi_calculated_signal = pyqtSignal(pd.DataFrame)
    stochastic_calculated_signal = pyqtSignal(pd.DataFrame)
    macd_calculated_signal = pyqtSignal(pd.DataFrame)
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        
    def calculate_sma(self, df, sma_period=10):
        try:
            if df is None:
                self.logger.log_or_print("data calculatro: recieved dataframes SMA calculation is None.", level="ERROR", module="MainLogic")
            self.logger.log_or_print("Starting SMA calculation...", level="INFO")
            
            df['SMA'] = ta.sma(df['Close'], length=sma_period).round(2)
            df['SMA10'] = ta.sma(df['Close'], length=10).round(2)
            df['SMA50'] = ta.sma(df['Close'], length=50).round(2)
            df['SMA200'] = ta.sma(df['Close'], length=200).round(2)

                # Golden Cross and Death Cross
            df['Golden_Cross'] = (df['SMA50'] > df['SMA200']) & (df['SMA50'].shift(1) <= df['SMA200'].shift(1))
            df['Death_Cross'] = (df['SMA50'] < df['SMA200']) & (df['SMA50'].shift(1) >= df['SMA200'].shift(1))
            df['Golden_Death_Cross_Desc'] = df.apply(
                lambda x: ("Golden Cross detected: This is a bullish signal where the shorter-term SMA50 crosses above the longer-term SMA200. " 
                        "Historically, this pattern has been seen during the early stages of a prolonged bull market. " 
                        "It might suggest that the asset's price will see an extended upward trajectory. " 
                        "As an investor, this can be a favorable time to consider adding to your position or entering a new buy trade.")
                if x['Golden_Cross'] 
                else ("Death Cross detected: This is a bearish signal indicating the potential beginning of a downward trend. "
                    "The shorter-term SMA50 has crossed below the longer-term SMA200, which might suggest a forthcoming bear market or a prolonged period of selling pressure. "
                    "It's often advisable to exercise caution, consider reducing exposure to the asset, or hedge against potential losses.")
                if x['Death_Cross'] 
                else ("No significant cross detected: Currently, the market is showing a neutral behavior with no clear bullish or bearish signals. "
                    "This can be a period of consolidation or sideways movement. It's essential to keep monitoring other indicators and stay updated with market news. "
                    "It might be wise to maintain a balanced and diversified strategy during such times."), axis=1)
            # Price and SMA10 Crossover
            df['Price_Cross_SMA10_Up'] = (df['Close'] > df['SMA10']) & (df['Close'].shift(1) <= df['SMA10'].shift(1))
            df['Price_Cross_SMA10_Down'] = (df['Close'] < df['SMA10']) & (df['Close'].shift(1) >= df['SMA10'].shift(1))
            # Price and SMA10 Crossover Descriptions
            df['Price_SMA10_Crossover_Desc'] = df.apply(
                lambda x: ("Price crossed above SMA10: This indicates a surge in short-term momentum as the asset's price surpasses its average over the last 10 periods. "
                        "Historically, such upward crossovers can hint at a short-term bullish trend. "
                        "Investors might interpret this as an opportunity to capitalize on this momentum, while also considering other technical indicators for confirmation.")
                if x['Price_Cross_SMA10_Up'] 
                else ("Price crossed below SMA10: This suggests a possible short-term decline as the price dips below its recent 10-period average. "
                    "It can be indicative of a potential pullback or a temporary bearish phase. Investors might consider this as a sign to be cautious, "
                    "potentially adjusting their short-term strategies or setting stop losses to protect gains.")
                if x['Price_Cross_SMA10_Down'] 
                else ("Price is oscillating around SMA10: The asset's price is currently interweaving with its 10-period average, indicating potential indecision in the market. "
                    "Such a pattern might point to a phase of consolidation, suggesting investors should stay alert, monitor other indicators, and be prepared for a breakout in either direction."),
                axis=1)
            # Price and SMA50 Crossovers
            df['Price_Cross_SMA50_Up'] = (df['Close'] > df['SMA50']) & (df['Close'].shift(1) <= df['SMA50'].shift(1))
            df['Price_Cross_SMA50_Down'] = (df['Close'] < df['SMA50']) & (df['Close'].shift(1) >= df['SMA50'].shift(1))
            df['Price_Crossover_Desc'] = df.apply(
                lambda x: ("Price crossed above SMA50: This indicates that recent price movements are showing bullish momentum as the asset's price has risen above its average over the last 50 periods. " 
                        "This could suggest a potential upward trend. Historically, when prices move above the SMA50, it's a sign of positive sentiment in the market. " 
                        "Investors might view this as a favorable time to enter the market or add to existing bullish positions.")
                if x['Price_Cross_SMA50_Up'] 
                else ("Price crossed below SMA50: The asset's price dropping below its 50-period average can be a sign of bearish momentum. "
                    "This may indicate a potential downtrend or a weakening in the asset's price strength. It can be a signal to investors to exercise caution. "
                    "Consider re-evaluating your position, setting stop losses, or even taking profits if you're already in a favorable position.")
                if x['Price_Cross_SMA50_Down'] 
                else ("Price is moving closely with SMA50: Currently, the asset's price is moving in tandem with its 50-period average, indicating a potential equilibrium in the market. "
                    "This might suggest a period of consolidation where neither the buyers nor sellers have significant control. "
                    "It's advisable to monitor other market indicators, news, and perhaps maintain a balanced strategy during such times."), axis=1)


            # Price and SMA200 Crossover
            df['Price_Cross_SMA200_Up'] = (df['Close'] > df['SMA200']) & (df['Close'].shift(1) <= df['SMA200'].shift(1))
            df['Price_Cross_SMA200_Down'] = (df['Close'] < df['SMA200']) & (df['Close'].shift(1) >= df['SMA200'].shift(1))
            # Price and SMA200 Crossover Descriptions
            df['Price_SMA200_Crossover_Desc'] = df.apply(
                lambda x: ("Price crossed above SMA200: A significant bullish signal as the asset's price moves above its long-term average of the past 200 periods. "
                        "This can often be interpreted as the commencement of a long-term upward trend. Historically, when prices ascend above the SMA200, the market sentiment tends to be bullish. "
                        "Investors might consider this a robust sign of the asset's potential and contemplate long-term investment strategies.")
                if x['Price_Cross_SMA200_Up'] 
                else ("Price crossed below SMA200: This denotes a potential long-term bearish trend as the asset's price descends below its 200-period average. "
                    "It's a warning signal that the asset might be entering a prolonged bearish phase. Investors should exercise caution, consider diversifying their portfolio, or look for hedging options.")
                if x['Price_Cross_SMA200_Down'] 
                else ("Price is meandering near SMA200: The asset's price is closely following its long-term average, suggesting a balance between buying and selling pressures. "
                    "This equilibrium might hint at a period of market consolidation. During such phases, investors might benefit from a wait-and-watch strategy, looking for stronger market signals."),
                axis=1)
            # SMA10 and SMA200 Crossover
            df['SMA10_Cross_SMA200_Up'] = (df['SMA10'] > df['SMA200']) & (df['SMA10'].shift(1) <= df['SMA200'].shift(1))
            df['SMA10_Cross_SMA200_Down'] = (df['SMA10'] < df['SMA200']) & (df['SMA10'].shift(1) >= df['SMA200'].shift(1))
            # SMA10 and SMA200 Crossover Descriptions
            df['SMA10_SMA200_Crossover_Desc'] = df.apply(
                lambda x: ("Golden Cross: The SMA10 crossed above SMA200, a bullish signal often seen as an indicator of a potential long-term upward trend. "
                        "Historically, the 'Golden Cross' has been a precursor to significant bullish phases. Investors might consider this a favorable sign for long-term investment opportunities, "
                        "but it's always wise to corroborate with other indicators.")
                if x['SMA10_Cross_SMA200_Up'] 
                else ("Death Cross: The SMA10 crossed below SMA200, typically perceived as a bearish sign, indicating a potential long-term downtrend. "
                    "Historically, the 'Death Cross' has been associated with prolonged bear markets. Investors might want to reassess their portfolios, considering defensive strategies or hedging against potential losses.")
                if x['SMA10_Cross_SMA200_Down'] 
                else ("SMA10 is closely tracking SMA200: The short-term and long-term averages are moving hand in hand, suggesting a balanced market momentum. "
                    "This can indicate a period of market consolidation or equilibrium. A breakout from this pattern can offer significant insights into the market's next move."),
                axis=1)
            # SMA Slopes
            df['SMA10_Up'] = df['SMA10'].diff() > 0
            df['SMA50_Up'] = df['SMA50'].diff() > 0
            df['SMA200_Up'] = df['SMA200'].diff() > 0
            df['SMA_Slopes_Desc'] = df.apply(
                lambda x: ("SMA10 Trending Upwards: The asset's recent price movements are favorable, indicating short-term bullish momentum. " 
                        "This could suggest that the current sentiment in the market is optimistic. For traders who focus on short-term movements, this might be a positive sign to monitor the asset closely.")
                if x['SMA10_Up'] 
                else ("SMA50 Trending Upwards: The asset's price is showing strength in the medium term, which can be a sign of sustained bullish momentum. "
                    "A rising SMA50 often indicates that the asset might be in an uptrend, and investors might consider this a positive sign for medium-term strategies.")
                if x['SMA50_Up'] 
                else ("SMA200 Trending Upwards: A rising SMA200 typically suggests a long-term bullish trend. "
                    "It's often seen as a strong indicator of the overall health of the asset in the broader market. For long-term investors, this might be an encouraging sign.")
                if x['SMA200_Up']
                else ("Neutral/Bearish Momentum Detected: Currently, the asset's short, medium, and long-term Simple Moving Averages (SMAs) aren't showing strong upward momentum. "
                    "This could suggest a period of consolidation, or even a potential downturn. It's advisable to exercise caution, monitor other market indicators, and perhaps adopt a defensive strategy."), axis=1)

            # Distance Between Price and SMA
            df['Price_Distance_SMA10'] = (df['Close'] - df['SMA10']).round(2)
            df['Price_Distance_SMA50'] = (df['Close'] - df['SMA50']).round(2)
            df['Price_Distance_SMA200'] = (df['Close'] - df['SMA200']).round(2)

            # SMA10 Description
            df['Price_Distance_SMA10_Desc'] = df.apply(
                lambda x: ("Short-Term Bullish Momentum: The asset's current price is above its short-term average, suggesting bullish momentum. "
                        "If the difference is too high, it might be approaching overbought conditions. Monitoring for potential pullbacks might be wise.")
                if x['Price_Distance_SMA10'] > 0 
                else ("Short-Term Bearish Momentum: The asset is trading below its short-term average, indicating potential bearish momentum. "
                    "If the difference is significant, it might be entering oversold territory, suggesting a possible buying opportunity soon.")
                if x['Price_Distance_SMA10'] < 0 
                else "Neutral Short-Term: The asset's price is trading near its short-term average, suggesting a balanced or consolidating market condition.",
                axis=1
            )

            # SMA50 Description
            df['Price_Distance_SMA50_Desc'] = df.apply(
                lambda x: ("Medium-Term Bullish Trend: The asset's price is above its medium-term average, indicating a potential bullish trend. "
                        "Consistent trading above the SMA50 can be a sign of strength. However, extreme deviations might suggest overvaluation.")
                if x['Price_Distance_SMA50'] > 0 
                else ("Medium-Term Bearish Trend: The asset's price is below its medium-term average, which can be a sign of a bearish trend. "
                    "A consistent deviation below SMA50 might indicate prolonged bearish sentiment or potential undervaluation.")
                if x['Price_Distance_SMA50'] < 0 
                else "Neutral Medium-Term: The asset's price is near its medium-term average, indicating potential consolidation or sideways movement.",
                axis=1
            )

            # SMA200 Description
            df['Price_Distance_SMA200_Desc'] = df.apply(
                lambda x: ("Long-Term Bullish Trend: The asset's price is above its long-term average, suggesting a sustained bullish trend. "
                        "Trading above the SMA200 typically indicates a strong market. Extreme deviations should be approached with caution as they can indicate bubbles.")
                if x['Price_Distance_SMA200'] > 0 
                else ("Long-Term Bearish Trend: The asset's price is below its long-term average, indicating a potential long-term bearish trend. "
                    "Trading consistently below the SMA200 can be a warning sign. However, significant undervaluation might present buying opportunities.")
                if x['Price_Distance_SMA200'] < 0 
                else "Neutral Long-Term: The asset's price is relatively close to its long-term average, suggesting stability and a lack of strong long-term trends.",
                axis=1
            )


            # Relationship Between SMA-10 and SMA-50
            df['SMA10_Above_SMA50'] = df['SMA10'] > df['SMA50']

            df['SMA_Relationship_10_50_Desc'] = df.apply(
                lambda x: ("Positive Momentum: The short-term average (SMA10) is above the medium-term average (SMA50). "
                        "This typically suggests a bullish momentum. Investors might consider this as a potential time to buy or hold their position. "
                        "However, it's essential to monitor other market indicators and ensure this isn't a brief upward spike.")
                if x['SMA10_Above_SMA50'] 
                else ("Negative Momentum: The short-term average (SMA10) is below the medium-term average (SMA50). "
                    "This can be a sign of bearish momentum. Investors might want to be cautious, consider taking profits, or waiting for a more favorable entry point. "
                    "Diversifying or hedging against potential downturns might also be an option to consider."),
                axis=1
            )

            # Relationship Between SMA-50 and SMA-200
            df['SMA50_Above_SMA200'] = df['SMA50'] > df['SMA200']

            df['SMA_Relationship_50_200_Desc'] = df.apply(
                lambda x: ("Strong Bullish Trend: The medium-term average (SMA50) is above the long-term average (SMA200). "
                        "Historically, this is a strong sign of a bullish market. Investors might view this as an encouraging sign to enter or remain in the market. "
                        "Nevertheless, it's prudent to continuously monitor other market indicators and be wary of potential market volatility.")
                if x['SMA50_Above_SMA200'] 
                else ("Potential Downtrend: The medium-term average (SMA50) is below the long-term average (SMA200). "
                    "This can indicate a bearish market trend. Investors may want to exercise caution, potentially reducing their exposure or seeking defensive positions. "
                    "Always consider the broader market context and other technical indicators before making investment decisions."),
                axis=1
            )

            
            self.logger.log_or_print("SMA calculation completed successfully.", level="INFO")
            if df is None:
                self.logger.log_or_print("data calculatro: Returned DataFrame from SMA calculation is None.", level="ERROR", module="MainLogic")
            self.sma_calculated_signal.emit(df)
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in calculate_sma: {str(e)}", level="ERROR", exc_info=True)
            self.sma_calculated_signal.emit(df)  # Return the original DataFrame if an error occurs
    def calculate_rsi(self, df):
        # Preliminary checks
        if df is None:
            self.logger.log_or_print("DataFrame is None in calculate_rsi", level="ERROR")
            self.rsi_calculated_signal.emit(df)
            return
        for period in [9, 14, 25]:
            try:
                self.logger.log_or_print(f"\n\n---------Starting RSI {period} Calculation---------", level="INFO")
                
                # Calculate RSI
                column_name = f"RSI_{period}"
                df[column_name] = ta.rsi(df["Close"], length=period).round(2)
                self.logger.log_or_print(f"\nDataFrame columns before flag creation: {df.columns}", level="INFO")
                # Boolean Interpretations
                df[f"{column_name}_Overbought_Flag"] = df[column_name] > 70
                df[f"{column_name}_Oversold_Flag"] = df[column_name] < 30
                df[f"{column_name}_Neutral_Flag"] = (df[column_name] >= 30) & (df[column_name] <= 70)
                df[f"{column_name}_Bearish_Divergence_Flag"] = (df['Close'].diff() > 0) & (df[column_name].diff() < 0) & (df[column_name] > 70)
                df[f"{column_name}_Bullish_Divergence_Flag"] = (df['Close'].diff() < 0) & (df[column_name].diff() > 0) & (df[column_name] < 30)
                df[f"{column_name}_Swing_Failure_Buy_Flag"] = (df[column_name] > 30) & (df[column_name].shift(1) < 30)
                df[f"{column_name}_Swing_Failure_Sell_Flag"] = (df[column_name] < 70) & (df[column_name].shift(1) > 70)
                self.logger.log_or_print(f"\nDataFrame columns after flag creation: {df.columns}", level="INFO")
                self.logger.log_or_print(f"\nColumn {column_name}_Bullish_Divergence_Flag values:", level="INFO")
                self.logger.log_or_print(str(df[f"{column_name}_Bullish_Divergence_Flag"].head(10)), level="INFO")  # log first 10 rows for this column
                # Descriptive Interpretations
                problem_rows = df[df[f"{column_name}_Bullish_Divergence_Flag"].isnull()]
                if not problem_rows.empty:
                    self.logger.log_or_print(f"Problematic rows:\n{problem_rows}", level="INFO")
                # RSI Overbought, Oversold
                df[f"{column_name}_Overbought_Oversold_Desc"] = df[column_name].apply(
                    lambda x: ("Overbought Territory: The RSI value exceeds 70, suggesting the asset might be overbought. "
                            "Historically, when the RSI remains above this level for an extended period, the asset may see a downward correction. "
                            "Investors might view this as a warning sign and consider reviewing their positions. "
                            "However, it's crucial to combine this with other technical indicators and market news before making any decisions.")
                    if x > 70 
                    else ("Oversold Territory: The RSI value is below 30, indicating the asset might be oversold. "
                        "Assets that remain in this territory for a while could be due for a rebound. "
                        "Investors might interpret this as a buying opportunity but should also be cautious of potential 'bear traps'. "
                        "It's recommended to use additional technical indicators and keep abreast of market news.")
                    if x < 30 
                    else ("Neutral Territory: The RSI is between 30 and 70, suggesting the asset is neither in an overbought nor oversold condition. "
                        "Investors might want to observe other market signals and indicators to gauge the asset's future movement. "
                        "Maintaining a balanced strategy and staying informed can be beneficial in this state.")
                )


                # RSI Divergences
                self.logger.log_or_print(f"Columns: {df.columns}", level="INFO")
                df[f"{column_name}_Divergence_Desc"] = df.apply(
                    lambda row: ("Bullish Divergence: The price makes a lower low, but the RSI forms a higher low. "
                                "This divergence suggests that while the price is dropping, the selling momentum is slowing down. "
                                "Historically, this pattern might precede a potential upward price reversal. "
                                "Investors could consider this as a sign to watch closely for buy signals. However, as always, it's crucial to use other technical indicators and market news to corroborate findings.")
                    if row.get(f"{column_name}_Bullish_Divergence_Flag")
                    else ("Bearish Divergence: The price records a higher high, but the RSI only manages a lower high. "
                        "This suggests that even though the price is rising, the buying momentum might be diminishing. "
                        "Historically, such a pattern might precede a potential price decline. "
                        "Investors might interpret this as a warning to review their positions and watch for sell signals. It's recommended to also consult other technical indicators and stay updated with market news.")
                    if row.get(f"{column_name}_Bearish_Divergence_Flag")
                    else ("No Divergence Detected: Both the price and the RSI are moving in tandem, indicating a strong and consistent trend. "
                        "Investors can interpret this as the current trend, whether bullish or bearish, being robust. It's advisable to continue monitoring other market signals and stay informed.")
                , axis=1
                )


                # RSI Swings
                df[f"{column_name}_Swings_Desc"] = df.apply(
                    lambda row: ("Bullish Swing Potential: The RSI has recently crossed above the 30 level. "
                                "This is often seen as an early signal that the asset might be reversing from its previous downtrend. "
                                "It suggests that the selling pressure could be decreasing, and the asset might start to gain upward momentum. "
                                "Investors could consider this as a potential buying opportunity but should also look for confirmation from other technical indicators or market news.")
                    if row.get(f"{column_name}_Swing_Failure_Buy_Flag")
                    else ("Bearish Swing Potential: The RSI has recently dipped below the 70 level. "
                        "This might indicate that the asset's prior uptrend could be slowing down, and a potential price pullback or reversal is on the horizon. "
                        "Investors might view this as a sign to be cautious, reassess their holdings, and watch for potential selling opportunities. It's essential to seek validation from other technical signals and be aware of overall market trends.")
                    if row.get(f"{column_name}_Swing_Failure_Sell_Flag")
                    else ("Neutral RSI Movement: Currently, there's no significant swing detected in the RSI. "
                        "The asset is moving without a clear bullish or bearish bias. It's recommended for investors to stay vigilant, monitor other technical patterns, and stay updated with market conditions.")
                , axis=1
                )

                self.logger.log_or_print(f"RSI {period} calculation and interpretation completed successfully.", level="INFO")
                self.rsi_calculated_signal.emit(df)
            except Exception as e:
                self.logger.log_or_print(f"An error occurred in calculate_rsi: {str(e)}", level="ERROR", exc_info=True)
                self.rsi_calculated_signal.emit(df)  # Emit the original/possibly partially modified DataFrame

    def calculate_stochastic_oscillator(self, df, k_period=9, d_period=6):
        try:
            if df is None:
                self.logger.log_or_print("DataFrame is None in calculate_stochastic_oscillator", level="ERROR")
                self.stochastic_calculated_signal.emit(None)
                return

            # Log initial DataFrame headers
            self.logger.log_or_print(f"Initial DataFrame columns: {df.columns.tolist()}", level="DEBUG")
            self.logger.log_or_print("Starting Stochastic Oscillator calculation...", level="INFO")

            stoch_df = ta.stoch(df['High'], df['Low'], df['Close'], k=k_period, d=d_period).round(2)
            for col in stoch_df.columns:
                df[col] = stoch_df[col]

            # Log headers and last column after stochastic calculation
            self.logger.log_or_print(f"Columns after stochastic calculation: {df.columns.tolist()}", level="DEBUG")
            self.logger.log_or_print(f"Last column after stochastic calculation:\n{df[df.columns[-1]].tail()}", level="DEBUG")

            # Column identifiers based on periods
            stoch_id = f"STOCH_{k_period}_{d_period}_3"

            # Flags
            df[f'{stoch_id}_Overbought_Flag'] = df[f'STOCHk_{k_period}_{d_period}_3'] > 80
            df[f'{stoch_id}_Oversold_Flag'] = df[f'STOCHk_{k_period}_{d_period}_3'] < 20
            df[f'{stoch_id}_Bullish_Crossover_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] > df[f'STOCHd_{k_period}_{d_period}_3']) & (df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) <= df[f'STOCHd_{k_period}_{d_period}_3'].shift(1))
            df[f'{stoch_id}_Bearish_Crossover_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] < df[f'STOCHd_{k_period}_{d_period}_3']) & (df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) >= df[f'STOCHd_{k_period}_{d_period}_3'].shift(1))
            df[f'{stoch_id}_Bullish_Divergence_Flag'] = (df['Low'].diff() < 0) & (df[f'STOCHk_{k_period}_{d_period}_3'].diff() > 0) & (df[f'STOCHk_{k_period}_{d_period}_3'] < 20)
            df[f'{stoch_id}_Bearish_Divergence_Flag'] = (df['High'].diff() > 0) & (df[f'STOCHk_{k_period}_{d_period}_3'].diff() < 0) & (df[f'STOCHk_{k_period}_{d_period}_3'] > 80)
            df[f'{stoch_id}_Midpoint_Cross_Up_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] > 50) & (df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) <= 50)
            df[f'{stoch_id}_Midpoint_Cross_Down_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] < 50) & (df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) >= 50)

            # Log headers and last column after setting flags
            self.logger.log_or_print(f"Columns after flag setting: {df.columns.tolist()}", level="DEBUG")
            self.logger.log_or_print(f"Last column after flag setting:\n{df[df.columns[-1]].tail()}", level="DEBUG")

            # Overbought/Oversold Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Overbought/Oversold_Desc'] = df.apply(
                lambda x: ("Overbought Alert: The Stochastic Oscillator is indicating that the asset might be overextended and is currently trading at a higher price than its intrinsic value. "
                        "This often suggests that there could be a potential price pullback or reversal in the near future. Investors might consider taking profits, tightening stop losses, or watching for signs of a trend reversal. "
                        "It's advised to cross-check with other technical indicators and market news before making a decision.")
                if x[f'{stoch_id}_Overbought_Flag']
                else ("Oversold Alert: The Stochastic Oscillator is suggesting that the asset might be undervalued and is currently trading at a lower price than its perceived value. "
                    "This can often be an indication that the asset might be due for a bounce back or price reversal upwards. Investors might view this as a potential buying opportunity, especially if they believe the asset's fundamentals are strong. "
                    "However, it's essential to ensure that the oversold condition isn't due to underlying problems with the asset. Always confirm with other technical indicators and stay updated with relevant news.")
                if x[f'{stoch_id}_Oversold_Flag']
                else ("Neutral Stochastic Readings: The asset's price movement is currently within a typical range as per the Stochastic Oscillator. "
                    "There are no immediate overbought or oversold signals. It's advised for investors to monitor other technical patterns, be observant for emerging trends, and stay informed on market news."),
                axis=1
            )
            # Divergence Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Divergence_Desc'] = df.apply(
                lambda x: ("Bullish Divergence Alert: The Stochastic Oscillator has identified a bullish divergence between the asset's price and its momentum. "
                        "This means that while the asset's price is making new lows, the Stochastic Oscillator isn't, suggesting potential weakening in the bearish trend. "
                        "This could indicate a potential reversal to the upside. Investors might consider this as an early signal to potentially enter a long position or hold off on selling. "
                        "However, it's crucial to confirm this signal with other technical indicators and ensure that the fundamentals of the asset support this bullish view.")
                if x[f'{stoch_id}_Bullish_Divergence_Flag']
                else ("Bearish Divergence Alert: The Stochastic Oscillator has spotted a bearish divergence between the asset's price and its momentum. "
                    "This means that while the asset's price is making new highs, the Stochastic Oscillator isn't, hinting at a potential weakening in the bullish momentum. "
                    "This divergence could foreshadow a potential price reversal to the downside. Investors might consider taking profits, setting a tighter stop loss, or preparing for a potential short entry. "
                    "Always validate this signal with other technical indicators and make sure to stay updated with any news related to the asset.")
                if x[f'{stoch_id}_Bearish_Divergence_Flag']
                else ("Neutral Divergence Readings: Currently, the Stochastic Oscillator hasn't identified any significant divergence between the asset's price and its momentum. "
                    "This typically indicates that the ongoing price trend, whether bullish or bearish, might persist. Investors are advised to keep monitoring the market for other technical patterns, stay observant for new divergences, and be informed on relevant market news."),
                axis=1
            )
            # Swing Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Swings_Desc'] = df.apply(
                lambda x: ("Bullish Crossover Alert: The Stochastic Oscillator has indicated a bullish crossover. This means the %K line has crossed above the %D line, suggesting a potential shift in momentum to the upside. "
                        "Investors might consider this as a buying opportunity, especially if the crossover occurred in the oversold territory. "
                        "However, always ensure that this signal aligns with other technical and fundamental indicators before making an investment decision.")
                if x[f'{stoch_id}_Bullish_Crossover_Flag']
                else ("Bearish Crossover Alert: The Stochastic Oscillator has signaled a bearish crossover. The %K line has crossed below the %D line, hinting at potential bearish momentum. "
                    "If this crossover occurred in the overbought zone, it might be a stronger signal for a potential pullback or downtrend. Investors might consider taking profits, setting a tighter stop loss, or preparing for a potential short entry. "
                    "Always corroborate this signal with other technical indicators and stay updated with any fundamental news or events related to the asset.")
                if x[f'{stoch_id}_Bearish_Crossover_Flag']
                else ("Midpoint Bullish Momentum: The Stochastic Oscillator has crossed above the midpoint (50), suggesting increased bullish momentum in the asset's price. "
                    "This might be an indication that the asset is gaining strength. Investors could consider this as a positive sign and potentially look for buying opportunities, especially if other indicators concur.")
                if x[f'{stoch_id}_Midpoint_Cross_Up_Flag']
                else ("Midpoint Bearish Momentum: The Stochastic Oscillator has crossed below the midpoint (50), signaling potential bearish momentum. "
                    "This might suggest that the asset is losing strength. Investors should exercise caution and potentially look for exit points or short-selling opportunities if other indicators align with this bearish view.")
                if x[f'{stoch_id}_Midpoint_Cross_Down_Flag']
                else ("Neutral Oscillator Readings: Currently, the Stochastic Oscillator hasn't identified any significant swings or crossovers. The asset might be in a consolidation phase, or the ongoing trend could continue without strong momentum shifts. "
                    "Investors are recommended to maintain a diversified strategy, monitor other technical indicators for corroborating signals, and stay informed on market news."),
                axis=1
            )


            # Log headers and last column after setting descriptions
            self.logger.log_or_print(f"Columns after setting descriptions: {df.columns.tolist()}", level="DEBUG")
            self.logger.log_or_print(f"Last column after setting descriptions:\n{df[df.columns[-1]].tail()}", level="DEBUG")

            self.logger.log_or_print("Stochastic Oscillator calculation and interpretation completed successfully.", level="INFO")
            self.stochastic_calculated_signal.emit(df)
        except Exception as e:
            self.logger.log_or_print(f"An error occurred in calculate_stochastic_oscillator: {str(e)}", level="ERROR", exc_info=True)
            self.stochastic_calculated_signal.emit(df)


