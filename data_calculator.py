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
    cmf_calculated_signal = pyqtSignal(pd.DataFrame)
    macd_calculated_signal = pyqtSignal(pd.DataFrame)
    obv_calculated_signal = pyqtSignal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def calculate_sma(self, df, sma_period=10):
        try:
            if df is None:
                self.logger.log_or_print(
                    "data calculatro: recieved dataframes SMA calculation is None.", level="ERROR", module="MainLogic")

            df['SMA'] = ta.sma(df['Close'], length=sma_period).round(2)
            df['SMA10'] = ta.sma(df['Close'], length=10).round(2)
            df['SMA50'] = ta.sma(df['Close'], length=50).round(2)
            df['SMA200'] = ta.sma(df['Close'], length=200).round(2)

            # Golden Cross and Death Cross
            df['Golden_Cross'] = (df['SMA50'] > df['SMA200']) & (
                df['SMA50'].shift(1) <= df['SMA200'].shift(1))
            df['Death_Cross'] = (df['SMA50'] < df['SMA200']) & (
                df['SMA50'].shift(1) >= df['SMA200'].shift(1))
            # Price and SMA10 Crossover
            df['Price_Cross_SMA10_Up'] = (df['Close'] > df['SMA10']) & (
                df['Close'].shift(1) <= df['SMA10'].shift(1))
            df['Price_Cross_SMA10_Down'] = (df['Close'] < df['SMA10']) & (
                df['Close'].shift(1) >= df['SMA10'].shift(1))
            # Price and SMA50 Crossovers
            df['Price_Cross_SMA50_Up'] = (df['Close'] > df['SMA50']) & (
                df['Close'].shift(1) <= df['SMA50'].shift(1))
            df['Price_Cross_SMA50_Down'] = (df['Close'] < df['SMA50']) & (
                df['Close'].shift(1) >= df['SMA50'].shift(1))
            # Price and SMA200 Crossover
            df['Price_Cross_SMA200_Up'] = (df['Close'] > df['SMA200']) & (
                df['Close'].shift(1) <= df['SMA200'].shift(1))
            df['Price_Cross_SMA200_Down'] = (df['Close'] < df['SMA200']) & (
                df['Close'].shift(1) >= df['SMA200'].shift(1))
            # SMA10 and SMA200 Crossover
            df['SMA10_Cross_SMA200_Up'] = (df['SMA10'] > df['SMA200']) & (
                df['SMA10'].shift(1) <= df['SMA200'].shift(1))
            df['SMA10_Cross_SMA200_Down'] = (df['SMA10'] < df['SMA200']) & (
                df['SMA10'].shift(1) >= df['SMA200'].shift(1))
            # SMA Slopes
            df['SMA10_Up'] = df['SMA10'].diff() > 0
            df['SMA50_Up'] = df['SMA50'].diff() > 0
            df['SMA200_Up'] = df['SMA200'].diff() > 0
            # Distance Between Price and SMA
            df['Price_Distance_SMA10'] = (df['Close'] - df['SMA10']).round(2)
            df['Price_Distance_SMA50'] = (df['Close'] - df['SMA50']).round(2)
            df['Price_Distance_SMA200'] = (df['Close'] - df['SMA200']).round(2)
            # Relationship Between SMA-50 and SMA-200
            df['SMA50_Above_SMA200'] = df['SMA50'] > df['SMA200']

            df['Golden_Death_Cross_Desc'] = df.apply(
                lambda x:
                ("Buy, Golden Cross Detected: The shorter-term SMA50 has crossed above the longer-term SMA200, a bullish signal. "
                 "Historically, this pattern indicates the early stages of a prolonged bull market. Interpretation: The asset's price might rise, suggesting a favorable time to buy or add to your position.")
                if x['Golden_Cross']
                else
                ("Sell, Death Cross Detected: The shorter-term SMA50 has crossed below the longer-term SMA200, a bearish signal. "
                 "This pattern often precedes a forthcoming bear market or a prolonged period of selling. Interpretation: Exercise caution, consider reducing exposure, or hedge against losses.")
                if x['Death_Cross']
                else
                ("Neutral, No Significant Cross Detected: The market shows no clear bullish or bearish signals at the moment. "
                 "This can indicate a period of consolidation or sideways movement. Interpretation: Monitor other indicators, stay updated with market news, and maintain a diversified strategy."),
                axis=1
            )

            # Price and SMA10 Crossover Descriptions
            df['Price_SMA10_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Price Crossed Above SMA10: The asset's price has surged above its 10-period average. "
                 "This upward crossover is historically a sign of short-term bullish momentum. Interpretation: It might be an opportunity to capitalize on the momentum, but also consider other indicators for confirmation.")
                if x['Price_Cross_SMA10_Up']
                else
                ("Sell, Price Crossed Below SMA10: The asset's price is dipping below its recent 10-period average. "
                 "This can hint at a short-term decline or a potential pullback. Interpretation: It might be wise to exercise caution, adjust strategies, or set stop losses.")
                if x['Price_Cross_SMA10_Down']
                else
                ("Neutral, Price Oscillating Around SMA10: The asset's price is weaving around its 10-period average, indicating market indecision. "
                 "This pattern could be a sign of consolidation. Interpretation: Stay alert, monitor other indicators, and be ready for a potential breakout."),
                axis=1
            )
            # Price  Crossover Descriptions
            df['Price_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Price Crossed Above SMA50: The asset's price has risen above its 50-period average, indicating bullish momentum. "
                 "Historically, prices above the SMA50 suggest positive market sentiment. Interpretation: It might be a favorable time to enter or add to bullish positions.")
                if x['Price_Cross_SMA50_Up']
                else
                ("Sell, Price Crossed Below SMA50: The asset's price has dropped below its 50-period average, signaling bearish momentum. "
                 "This could indicate a potential downtrend or weakening price strength. Interpretation: It's wise to exercise caution, possibly re-evaluate positions or set stop losses.")
                if x['Price_Cross_SMA50_Down']
                else
                ("Neutral, Price Moving with SMA50: The asset's price is in line with its 50-period average, suggesting market equilibrium. "
                 "This pattern might point to consolidation, where neither buyers nor sellers dominate. Interpretation: Monitor other indicators, stay updated with news, and maintain a balanced strategy."),
                axis=1
            )

            # Price and SMA200 Crossover Descriptions
            df['Price_SMA200_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Price Crossed Above SMA200, "
                 "The asset's price has surpassed its long-term 200-period average, signaling a notable bullish trend. Historically, an ascent above the SMA200 has been associated with bullish market sentiment, "
                 "This might be a robust indication of the asset's potential, suggesting consideration for long-term investment.")
                if x['Price_Cross_SMA200_Up']
                else
                ("Sell, Price Crossed Below SMA200, "
                 "The asset's price has dropped below its long-term 200-period average, indicating a potential prolonged bearish phase. This descent is a cautionary signal of a possible extended bearish trend, "
                 "Investors should be cautious, think about diversifying, or explore hedging options.")
                if x['Price_Cross_SMA200_Down']
                else
                ("Neutral, Price Oscillating Near SMA200, "
                 "The asset's price is closely aligned with its 200-period average, suggesting equilibrium between buying and selling forces. This balance might indicate a consolidation phase, "
                 "In such scenarios, a wait-and-observe approach could be beneficial, while awaiting stronger market cues."),
                axis=1
            )

            # SMA10 and SMA200 Crossover Descriptions
            df['SMA10_SMA200_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Golden Cross Detected Between SMA10 and SMA200, "
                 "The shorter-term SMA10 has surpassed the longer-term SMA200, often interpreted as a bullish signal hinting at a potential long-term upward trajectory. Historically, the 'Golden Cross' has signified the onset of extended bullish phases, "
                 "This event can be perceived as a positive sign for long-term investments, but it's recommended to cross-reference with other indicators.")
                if x['SMA10_Cross_SMA200_Up']
                else
                ("Sell, Death Cross Detected Between SMA10 and SMA200, "
                 "The shorter-term SMA10 has descended below the longer-term SMA200, commonly viewed as a bearish sign suggesting a potential prolonged downtrend. Historically, the 'Death Cross' has been a harbinger of extended bear markets, "
                 "Investors should contemplate re-evaluating their positions, potentially adopting defensive strategies or considering hedging measures.")
                if x['SMA10_Cross_SMA200_Down']
                else
                ("Neutral, SMA10 Oscillating Near SMA200, "
                 "Both the short-term and long-term moving averages are moving in tandem, indicating a period of balanced market momentum. This behavior suggests a possible phase of market consolidation or equilibrium, "
                 "Awaiting a breakout from this pattern might provide pivotal insights into the forthcoming market direction."),
                axis=1
            )
            # SMA Slops Descriptions
            df['SMA_Slopes_Desc'] = df.apply(
                lambda x:
                ("Buy, SMA10 Trending Upwards, "
                 "The recent price movements of the asset are favorable, which may indicate short-term bullish momentum. "
                 "For traders focused on short-term movements, this could be a cue to monitor the asset more closely, anticipating potential opportunities.")
                if x['SMA10_Up']
                else
                ("Buy, SMA50 Trending Upwards, "
                 "The asset's price showcases strength in the medium term, possibly hinting at sustained bullish momentum. "
                 "A rising SMA50 often suggests the asset might be on an uptrend, which can be interpreted as a favorable sign for medium-term investment strategies.")
                if x['SMA50_Up']
                else
                ("Buy, SMA200 Trending Upwards, "
                 "The SMA200, representing long-term trends, is on the rise, often interpreted as a sign of a long-term bullish trend. "
                 "This trend can be a strong indication of the asset's overall health in the broader market, potentially signaling positive prospects for long-term investors.")
                if x['SMA200_Up']
                else
                ("Neutral, No Strong Upward Momentum in SMAs Detected, "
                 "The asset's short, medium, and long-term Simple Moving Averages (SMAs) aren't displaying significant upward trends. "
                 "This pattern could hint at a phase of market consolidation or a potential downturn, suggesting a cautious approach and monitoring of other market indicators."),
                axis=1
            )

            # SMA10 Description
            df['Price_Distance_SMA10_Desc'] = df.apply(
                lambda x:
                ("Buy, Short-Term Bullish Momentum, "
                 "The asset's current price is above its short-term average, indicating bullish momentum. "
                 "If the price difference from the SMA10 is substantial, it might be nearing overbought conditions, suggesting the need to monitor for possible retracements.")
                if x['Price_Distance_SMA10'] > 0
                else
                ("Sell, Short-Term Bearish Momentum, "
                 "The asset's price is below its short-term average, signaling potential bearish momentum. "
                 "A significant negative difference from the SMA10 could hint at the asset being oversold, potentially offering a buying opportunity in the near future.")
                if x['Price_Distance_SMA10'] < 0
                else
                ("Neutral, Asset Price Near SMA10, "
                 "The asset's price is trading around its short-term average, indicating a balanced or consolidating market condition. "
                 "In such scenarios, it's often beneficial to monitor other indicators and market news for clearer direction."),
                axis=1
            )

            # SMA50 Description
            df['Price_Distance_SMA50_Desc'] = df.apply(
                lambda x:
                ("Buy, Medium-Term Bullish Trend, "
                 "The asset's price is above its medium-term average, suggesting a bullish momentum. "
                 "While consistent trading above the SMA50 can denote strength, significant deviations might point towards overvaluation, warranting a more cautious approach.")
                if x['Price_Distance_SMA50'] > 0
                else
                ("Sell, Medium-Term Bearish Trend, "
                 "The asset's price is below its medium-term average, which can be an indication of bearish sentiment. "
                 "Trading considerably below the SMA50 might imply a sustained bearish phase or a potential undervalued state, which could be an opportunity for value investors.")
                if x['Price_Distance_SMA50'] < 0
                else
                ("Neutral, Near Medium-Term Average, "
                 "The asset's price is oscillating around its medium-term average, suggesting potential consolidation or a period of sideways trading. "
                 "In such phases, observing other technical indicators and market news can provide additional insights."),
                axis=1
            )

            # SMA200 Description
            df['Price_Distance_SMA200_Desc'] = df.apply(
                lambda x:
                ("Buy, Long-Term Bullish Trend, "
                 "The asset's price is trading above its long-term average. "
                 "Being above the SMA200 generally signifies a strong market. However, significant deviations might suggest overextended rallies or bubbles, so it's advisable to tread cautiously.")
                if x['Price_Distance_SMA200'] > 0
                else
                ("Sell, Long-Term Bearish Trend, "
                 "The asset's price is trading below its long-term average. "
                 "Consistently trading below the SMA200 can be a cause for concern. On the flip side, extreme undervaluation might signal a buying opportunity.")
                if x['Price_Distance_SMA200'] < 0
                else
                ("Neutral, In Line With Long-Term Average, "
                 "The asset's price is hovering around its long-term average. "
                 "Such conditions denote stability and the lack of strong long-term biases, suggesting the need to monitor other market indicators for a clearer picture."),
                axis=1
            )

            # Relationship Between SMA-10 and SMA-50
            df['SMA10_Above_SMA50'] = df['SMA10'] > df['SMA50']

            df['SMA_Relationship_10_50_Desc'] = df.apply(
                lambda x:
                ("Buy, Positive Short to Medium-Term Momentum, "
                 "The short-term average (SMA10) is currently above the medium-term average (SMA50), suggesting bullish momentum in the market. "
                 "While this might be seen as a favorable time to buy or hold positions, it's crucial to monitor other market indicators to ensure this isn't a fleeting upward spike.")
                if x['SMA10_Above_SMA50']
                else
                ("Sell, Negative Short to Medium-Term Momentum, "
                 "The short-term average (SMA10) is trading below the medium-term average (SMA50), indicating potential bearish momentum. "
                 "Investors might want to exercise caution, possibly re-evaluating their positions or looking for a more opportune entry point. Adopting defensive strategies or considering hedging options might be wise."),
                axis=1
            )

            df['SMA_Relationship_50_200_Desc'] = df.apply(
                lambda x:
                ("Buy, Strong Medium to Long-Term Bullish Trend, "
                 "The medium-term average (SMA50) is currently positioned above the long-term average (SMA200), signifying a dominant bullish trend in the market. "
                 "Historically, this pattern is seen as an indicator of a continuing upward market trajectory. However, it's essential to remain vigilant and monitor other market indicators to anticipate any sudden shifts or volatilities.")
                if x['SMA50_Above_SMA200']
                else
                ("Sell, Potential Medium to Long-Term Downtrend, "
                 "The medium-term average (SMA50) is below the long-term average (SMA200), hinting at a potential bearish trend in the market. "
                 "This configuration might be a signal for investors to reassess their market stance, possibly considering defensive measures or reducing exposure. As always, integrating insights from other market indicators and the broader market context is advisable before finalizing decisions."),
                axis=1
            )

            # Initialize consolidated recommendation count columns
            df['SMA_Buy_Count'] = 0
            df['SMA_Sell_Count'] = 0
            df['SMA_Neutral_Count'] = 0

            # List of SMA Description Columns
            desc_columns = ['Golden_Death_Cross_Desc', 'Price_SMA10_Crossover_Desc', 'Price_Crossover_Desc',
                            'Price_SMA200_Crossover_Desc', 'SMA10_SMA200_Crossover_Desc', 'SMA_Slopes_Desc',
                            'Price_Distance_SMA10_Desc', 'Price_Distance_SMA50_Desc', 'Price_Distance_SMA200_Desc',
                            'SMA_Relationship_10_50_Desc', 'SMA_Relationship_50_200_Desc']

            # Iterate Over Each Column and aggregate counts
            for column in desc_columns:
                df['SMA_Buy_Count'] += df[column].str.startswith(
                    "Buy").astype(int)
                df['SMA_Sell_Count'] += df[column].str.startswith(
                    "Sell").astype(int)
                df['SMA_Neutral_Count'] += df[column].str.startswith(
                    "Neutral").astype(int)

            if df is None:
                self.logger.log_or_print(
                    "data calculatro: Returned DataFrame from SMA calculation is None.", level="ERROR", module="MainLogic")
            self.sma_calculated_signal.emit(df)
        except Exception as e:
            self.logger.log_or_print(
                f"An error occurred in calculate_sma: {str(e)}", level="ERROR", exc_info=True)
            # Return the original DataFrame if an error occurs
            self.sma_calculated_signal.emit(df)

    def calculate_rsi(self, df):
        # Preliminary checks
        if df is None:

            self.rsi_calculated_signal.emit(df)
            return
        for period in [9, 14, 25]:
            try:

                # Calculate RSI
                column_name = f"RSI_{period}"
                df[column_name] = ta.rsi(df["Close"], length=period).round(2)

                # Boolean Interpretations
                df[f"{column_name}_Overbought_Flag"] = df[column_name] > 70
                df[f"{column_name}_Oversold_Flag"] = df[column_name] < 30
                df[f"{column_name}_Neutral_Flag"] = (
                    df[column_name] >= 30) & (df[column_name] <= 70)
                df[f"{column_name}_Bearish_Divergence_Flag"] = (df['Close'].diff() > 0) & (
                    df[column_name].diff() < 0) & (df[column_name] > 70)
                df[f"{column_name}_Bullish_Divergence_Flag"] = (df['Close'].diff() < 0) & (
                    df[column_name].diff() > 0) & (df[column_name] < 30)
                df[f"{column_name}_Swing_Failure_Buy_Flag"] = (
                    df[column_name] > 30) & (df[column_name].shift(1) < 30)
                df[f"{column_name}_Swing_Failure_Sell_Flag"] = (
                    df[column_name] < 70) & (df[column_name].shift(1) > 70)

                # Descriptive Interpretations
                problem_rows = df[df[f"{column_name}_Bullish_Divergence_Flag"].isnull(
                )]
                if not problem_rows.empty:
                    self.logger.log_or_print(
                        f"Problematic rows:\n{problem_rows}", level="INFO")
                # RSI Overbought, Oversold
                df[f"{column_name}_Overbought_Oversold_Desc"] = df[column_name].apply(
                    lambda x:
                    ("Sell, Overbought Territory, "
                     "The RSI value is currently above 70, indicating that the asset may be overbought. Historically, an RSI value remaining above this level might suggest an impending downward correction. "
                     "Although this can serve as a cautionary signal for investors, it's imperative to integrate insights from other technical indicators and market news before making investment decisions.")
                    if x > 70
                    else
                    ("Buy, Oversold Territory, "
                     "The RSI value is below 30, which typically suggests that the asset may be undervalued or oversold. Assets with prolonged periods in this zone might be gearing up for a rebound. "
                     "While this can be seen as a potential buying opportunity, it's essential to be wary of false positives or 'bear traps'. Augmenting this analysis with other indicators and staying updated with market news is crucial.")
                    if x < 30
                    else
                    ("Neutral, Neutral RSI Territory, "
                     "The RSI value lies between 30 and 70, indicating that the asset is neither overbought nor oversold. In such situations, it's beneficial for investors to monitor other market signals and trends. "
                     "Maintaining a diversified strategy and staying informed can provide a competitive edge.")
                )

                # RSI Divergences
                df[f"{column_name}_Divergence_Desc"] = df.apply(
                    lambda row:
                    ("Buy, Bullish Divergence, "
                     "The current price trend is making a lower low, but the RSI is observing a higher low. This divergence often indicates a slowing selling momentum despite the dropping price. "
                     "Historically, such patterns have been associated with potential upward price reversals. As a possible turning point, investors might want to closely monitor for additional buy signals while also considering other technical indicators and market updates.")
                    if row.get(f"{column_name}_Bullish_Divergence_Flag")
                    else
                    ("Sell, Bearish Divergence, "
                     "The price trend is achieving a higher high, whereas the RSI is only reaching a lower high. This divergence can indicate a weakening buying momentum even as the price continues to rise. "
                     "Historically, such scenarios may hint at upcoming price declines. Investors might interpret this as a sign to reassess their positions, look out for potential sell signals, and also factor in insights from other technical indicators and market news.")
                    if row.get(f"{column_name}_Bearish_Divergence_Flag")
                    else
                    ("Neutral, No Divergence Detected, "
                     "Both the price and the RSI are synchronously moving, suggesting a consistent trend. Such a movement usually signifies that the prevailing trend, be it bullish or bearish, remains solid. "
                     "In such scenarios, it's beneficial to stay updated with other market indicators and relevant news."), axis=1)

                # RSI Swings
                df[f"{column_name}_Swings_Desc"] = df.apply(
                    lambda row:
                    ("Buy, Bullish Swing Potential, "
                     "The RSI has just surpassed the 30 mark, often viewed as a hint of a potential upward reversal from a prior downtrend. "
                     "Such movements suggest the ebbing of selling pressure, possibly paving the way for rising momentum. Investors might interpret this as an early buying cue but should seek corroborative evidence from other technical indicators and pertinent market news.")
                    if row.get(f"{column_name}_Swing_Failure_Buy_Flag")
                    else
                    ("Sell, Bearish Swing Potential, "
                     "The RSI has recently descended below the 70 threshold, hinting at a possible wane in the asset's preceding uptrend and signaling a potential price retraction or flip. "
                     "This might be a juncture for investors to exercise prudence, re-evaluate their positions, and be on the lookout for potential exit points. As always, juxtaposing this with other technical signals and tracking overarching market trends is crucial.")
                    if row.get(f"{column_name}_Swing_Failure_Sell_Flag")
                    else
                    ("Neutral, Stable RSI Trajectory, "
                     "At present, the RSI is not indicating any pronounced swings, showcasing neither a clear bullish nor bearish inclination. In such states, investors might benefit from a vigilant stance, tracking other technical patterns, and staying abreast of market dynamics."), axis=1)
                # Count the number of Buy, Sell, and Neutral recommendations for each period
                df[f"{column_name}_Buy_Count"] = df[f"{column_name}_Overbought_Oversold_Desc"].str.startswith(
                    "Buy").astype(int)
                df[f"{column_name}_Sell_Count"] = df[f"{column_name}_Overbought_Oversold_Desc"].str.startswith(
                    "Sell").astype(int)
                df[f"{column_name}_Neutral_Count"] = df[f"{column_name}_Overbought_Oversold_Desc"].str.startswith(
                    "Neutral").astype(int)

                # Summing the counts for Divergence and Swings descriptions as well
                df[f"{column_name}_Buy_Count"] += df[f"{column_name}_Divergence_Desc"].str.startswith(
                    "Buy").astype(int)
                df[f"{column_name}_Sell_Count"] += df[f"{column_name}_Divergence_Desc"].str.startswith(
                    "Sell").astype(int)
                df[f"{column_name}_Neutral_Count"] += df[f"{column_name}_Divergence_Desc"].str.startswith(
                    "Neutral").astype(int)

                df[f"{column_name}_Buy_Count"] += df[f"{column_name}_Swings_Desc"].str.startswith(
                    "Buy").astype(int)
                df[f"{column_name}_Sell_Count"] += df[f"{column_name}_Swings_Desc"].str.startswith(
                    "Sell").astype(int)
                df[f"{column_name}_Neutral_Count"] += df[f"{column_name}_Swings_Desc"].str.startswith(
                    "Neutral").astype(int)

                self.rsi_calculated_signal.emit(df)
            except Exception as e:
                self.logger.log_or_print(
                    f"An error occurred in calculate_rsi: {str(e)}", level="ERROR", exc_info=True)
                # Emit the original/possibly partially modified DataFrame
                self.rsi_calculated_signal.emit(df)

    def calculate_stochastic_oscillator(self, df, k_period=9, d_period=6):
        try:
            if df is None:
                self.logger.log_or_print(
                    "DataFrame is None in calculate_stochastic_oscillator", level="ERROR")
                self.stochastic_calculated_signal.emit(None)
                return

            # Log initial DataFrame headers

            stoch_df = ta.stoch(df['High'], df['Low'],
                                df['Close'], k=k_period, d=d_period).round(2)
            for col in stoch_df.columns:
                df[col] = stoch_df[col]

            # Column identifiers based on periods
            stoch_id = f"STOCH_{k_period}_{d_period}_3"

            # Flags
            df[f'{stoch_id}_Overbought_Flag'] = df[f'STOCHk_{k_period}_{d_period}_3'] > 80
            df[f'{stoch_id}_Oversold_Flag'] = df[f'STOCHk_{k_period}_{d_period}_3'] < 20
            df[f'{stoch_id}_Bullish_Crossover_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] > df[f'STOCHd_{k_period}_{d_period}_3']) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) <= df[f'STOCHd_{k_period}_{d_period}_3'].shift(1))
            df[f'{stoch_id}_Bearish_Crossover_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] < df[f'STOCHd_{k_period}_{d_period}_3']) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) >= df[f'STOCHd_{k_period}_{d_period}_3'].shift(1))
            df[f'{stoch_id}_Bullish_Divergence_Flag'] = (df['Low'].diff() < 0) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].diff() > 0) & (df[f'STOCHk_{k_period}_{d_period}_3'] < 20)
            df[f'{stoch_id}_Bearish_Divergence_Flag'] = (df['High'].diff() > 0) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].diff() < 0) & (df[f'STOCHk_{k_period}_{d_period}_3'] > 80)
            df[f'{stoch_id}_Midpoint_Cross_Up_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] > 50) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) <= 50)
            df[f'{stoch_id}_Midpoint_Cross_Down_Flag'] = (df[f'STOCHk_{k_period}_{d_period}_3'] < 50) & (
                df[f'STOCHk_{k_period}_{d_period}_3'].shift(1) >= 50)

            # Overbought/Oversold Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Overbought/Oversold_Desc'] = df.apply(
                lambda x:
                ("Sell, Overbought Condition, "
                 "The Stochastic Oscillator is signaling that the asset may be trading at a price significantly higher than its intrinsic value. "
                 "Historical data often indicates that such conditions can lead to potential price retractions or reversals. Action: Investors might consider taking profits, setting tighter stop-loss levels, or watching for signs of a trend reversal, ensuring to validate with other indicators and stay updated on market news.")
                if x[f'{stoch_id}_Overbought_Flag']
                else
                ("Buy, Oversold Condition, "
                 "The Stochastic Oscillator suggests the asset could be trading at a price notably lower than its perceived value. "
                 "Such readings often imply a possible upward price correction or reversal in the near future. Action: Investors might view this as an opportunity to buy, especially if they have confidence in the asset's fundamentals. However, ensuring the oversold condition isn't due to intrinsic problems with the asset is crucial. It's always wise to cross-check with other indicators and monitor relevant news.")
                if x[f'{stoch_id}_Oversold_Flag']
                else
                ("Neutral, Stable Stochastic Range, "
                 "The Stochastic Oscillator indicates that the asset's price movement is within its typical range, not showing clear overbought or oversold signs. "
                 "This suggests a phase of balance in the market. Action: Investors should keep a close eye on other technical patterns, be ready for emerging trends, and stay informed on market news."), axis=1)

            # Divergence Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Divergence_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Divergence Detected, "
                 "The Stochastic Oscillator is highlighting a bullish divergence where the asset's price is recording new lows but the momentum indicator isn't. "
                 "Historically, this indicates potential weakening of the bearish trend, possibly hinting at a future upside reversal. Action: Investors might consider this as an opportunity to buy or to hold off from selling. It's essential to validate this signal with other indicators and ensure the asset's fundamentals align with a bullish perspective.")
                if x[f'{stoch_id}_Bullish_Divergence_Flag']
                else
                ("Sell, Bearish Divergence Detected, "
                 "The Stochastic Oscillator is showcasing a bearish divergence; while the asset's price is achieving new highs, the momentum indicator isn't keeping up. "
                 "This often suggests a potential decline in bullish momentum and could foretell a bearish price reversal. Action: Investors might think about realizing profits, setting tighter stop-loss levels, or preparing for a potential short position. It's crucial to corroborate this signal with other technical patterns and to be aware of any asset-related news.")
                if x[f'{stoch_id}_Bearish_Divergence_Flag']
                else
                ("Neutral, No Divergence Observed, "
                 "The Stochastic Oscillator doesn't pinpoint any significant divergence between the asset's price and its momentum at the moment. "
                 "This typically means the ongoing trend, whether bullish or bearish, may continue. Action: Investors should stay vigilant, observe other market signals, and be ready for potential emerging divergences."), axis=1)

            # Swing Descriptions for Stochastic Oscillator
            df[f'{stoch_id}_Swings_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Crossover Detected, "
                 "The Stochastic Oscillator has showcased a bullish crossover with the %K line moving above the %D line, indicating a potential upward shift in momentum. "
                 "Historically, this hints at a potential buying opportunity, especially if the crossover occurred in oversold conditions. Action: Investors might consider entering a long position, but it's essential to validate this signal with other indicators and market news.")
                if x[f'{stoch_id}_Bullish_Crossover_Flag']
                else
                ("Sell, Bearish Crossover Detected, "
                 "The Stochastic Oscillator points to a bearish crossover, with the %K line moving below the %D line, suggesting possible bearish momentum. "
                 "If this crossover took place in the overbought region, it could strengthen the case for a potential pullback. Action: Investors might think about realizing profits or preparing for a potential short entry. Always cross-reference this signal with other technical indicators and current market conditions.")
                if x[f'{stoch_id}_Bearish_Crossover_Flag']
                else
                ("Buy, Midpoint Bullish Momentum, "
                 "The Stochastic Oscillator has risen above the midpoint (50), implying a surge in bullish momentum. "
                 "Historically, this indicates the asset is gaining strength. Action: Investors might view this as a potential buying opportunity, especially if other technical patterns support this bullish view.")
                if x[f'{stoch_id}_Midpoint_Cross_Up_Flag']
                else
                ("Sell, Midpoint Bearish Momentum, "
                 "The Stochastic Oscillator has dipped below the midpoint (50), indicating potential bearish momentum. "
                 "This could suggest the asset's strength is waning. Action: Investors should consider reviewing their positions, potentially looking for exit points or short-selling opportunities if other indicators support this bearish perspective.")
                if x[f'{stoch_id}_Midpoint_Cross_Down_Flag']
                else
                ("Neutral, No Significant Swings Observed, "
                 "The Stochastic Oscillator hasn't pinpointed any notable swings or crossovers, suggesting the asset might be consolidating or the current trend could persist without robust momentum shifts. "
                 "Action: Investors should adopt a balanced approach, keep an eye on other technical signals, and stay updated with market news."), axis=1)
            # Initialize consolidated recommendation count columns
            df[f'{stoch_id}_Buy_Count'] = 0
            df[f'{stoch_id}_Sell_Count'] = 0
            df[f'{stoch_id}_Neutral_Count'] = 0

            # List of Stochastic Description Columns
            desc_columns_stoch = [f'{stoch_id}_Overbought/Oversold_Desc',
                                  f'{stoch_id}_Divergence_Desc',
                                  f'{stoch_id}_Swings_Desc']

            # Iterate Over Each Column and aggregate counts
            for column in desc_columns_stoch:
                df[f'{stoch_id}_Buy_Count'] += df[column].str.startswith(
                    "Buy").astype(int)
                df[f'{stoch_id}_Sell_Count'] += df[column].str.startswith(
                    "Sell").astype(int)
                df[f'{stoch_id}_Neutral_Count'] += df[column].str.startswith(
                    "Neutral").astype(int)

            self.stochastic_calculated_signal.emit(df)
        except Exception as e:
            self.logger.log_or_print(
                f"An error occurred in calculate_stochastic_oscillator: {str(e)}", level="ERROR", exc_info=True)
            self.stochastic_calculated_signal.emit(df)

    def calculate_cmf(self, df, window=20):
        try:
            if df is None:

                self.cmf_calculated_signal.emit(None)
                return

            # Ensure data is sorted by date in ascending order
            # df = df.sort_values(by='Date')
            delta = df['High'] - df['Low']
            zero_delta_indices = delta[delta == 0].index
            if len(zero_delta_indices) > 0:
                self.logger.log_or_print(
                    f"Identified rows with zero high-low difference at indices: {zero_delta_indices.tolist()}", level="WARNING")
            # replace 0 with a small number to avoid division by zero
            delta.replace({0: 0.0001}, inplace=True)
            # Money Flow Multiplier (MFM)

            MFM = ((df['Close'] - df['Low']) -
                   (df['High'] - df['Close'])) / delta
            # Money Flow Volume (MFV)
            MFV = MFM * df['T.Shares']
            # CMF
            df['CMF_' + str(window)] = ((MFV.rolling(window=window).sum() /
                                         df['T.Shares'].rolling(window=window).sum())).round(2)

            # Flags
            df['CMF_Positive_Flag'] = df['CMF_' + str(window)] > 0
            df['CMF_Negative_Flag'] = df['CMF_' + str(window)] < 0
            df['CMF_Neutral_Flag'] = df['CMF_' + str(window)] == 0
            df['CMF_Zero_Crossover_Up_Flag'] = (
                df['CMF_' + str(window)] > 0) & (df['CMF_' + str(window)].shift(1) <= 0)
            df['CMF_Zero_Crossover_Down_Flag'] = (
                df['CMF_' + str(window)] < 0) & (df['CMF_' + str(window)].shift(1) >= 0)
            df['CMF_Above_SMA50_Flag'] = df['CMF_' + str(window)] > df['SMA50']
            df['CMF_Below_SMA50_Flag'] = df['CMF_' + str(window)] < df['SMA50']
            df['CMF_Overbought_Flag'] = df['CMF_' + str(window)] > 0.25
            df['CMF_Oversold_Flag'] = df['CMF_' + str(window)] < -0.25
            df['CMF_Bullish_Divergence_Flag'] = (df['Low'].diff() < 0) & (
                df['CMF_' + str(window)].diff() > 0)
            df['CMF_Bearish_Divergence_Flag'] = (df['High'].diff() > 0) & (
                df['CMF_' + str(window)].diff() < 0)

        # Interpretations and Recommendations
            df['CMF_Value_Range_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish CMF Value Detected, "
                 "The Chaikin Money Flow (CMF) value is in the positive range, indicating that buying pressure has been dominant over the defined period. "
                 "Historically, a positive CMF suggests a bullish sentiment in the market. Action: Consider potential long positions or holding current longs. As always, corroborate with other technical indicators before making any decisions.")
                if x['CMF_Positive_Flag']
                else
                ("Sell, Bearish CMF Value Detected, "
                 "The CMF value is in the negative range, indicating that selling pressure has been more dominant over the defined period. "
                 "Historically, a negative CMF often suggests a bearish sentiment in the market. Action: Consider potential short positions, exiting current longs, or adopting defensive strategies. Monitoring resistance levels and other technical indicators can be beneficial.")
                if x['CMF_Negative_Flag']
                else
                ("Neutral, CMF Value Near Zero, "
                 "The CMF value is near zero, indicating a balance between buying and selling pressures, which can signify market indecision or equilibrium over the defined period. "
                 "Action: Adopt a wait-and-see approach, and monitor the asset for potential breakout or breakdown patterns. Corroborating with other technical indicators can provide a clearer market outlook."), axis=1)

            df['CMF_Zero_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Zero-Line Crossover Detected, "
                 "The Chaikin Money Flow (CMF) has crossed above the zero line, typically suggesting increased buying pressure. "
                 "Historically, this crossover can be a bullish signal indicating potential upward momentum in the asset's price. Action: Consider buying, especially if supported by other bullish indicators and market news.")
                if x['CMF_Zero_Crossover_Up_Flag']
                else
                ("Sell, Bearish Zero-Line Crossover Detected, "
                 "The CMF has crossed below the zero line, often indicating increased selling pressure or potential bearish momentum in the market. "
                 "Historically, this crossover can be a bearish signal, suggesting a potential decline in the asset's price. Action: Consider selling, hedging, or reducing long positions, especially if the bearish view is confirmed by other technical indicators.")
                if x['CMF_Zero_Crossover_Down_Flag']
                else
                ("Neutral, CMF Near Zero Line, "
                 "The CMF is hovering around the zero line, suggesting equilibrium between buying and selling pressures. "
                 "Action: Monitor for potential shifts in momentum, and corroborate with other technical indicators for a clearer market perspective."), axis=1)

            df['CMF_SMA_Comparison_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Trend Relative to SMA50 Detected, "
                 "The Chaikin Money Flow (CMF) is above the SMA50, suggesting that the asset's short-term momentum is outpacing its medium-term trend. "
                 "Historically, this configuration can indicate bullish momentum. Action: Reinforce or enter long positions but set a stop-loss near key support levels.")
                if x['CMF_Above_SMA50_Flag']
                else
                ("Sell, Bearish Trend Relative to SMA50 Detected, "
                 "The CMF is below the SMA50, indicating that the asset's short-term momentum is weaker than its medium-term trend. "
                 "Historically, this can be a sign of bearish momentum. Action: Exercise caution with long positions. Consider hedging, shorting, or reducing exposure if other indicators align bearishly.")
                if x['CMF_Below_SMA50_Flag']
                else
                ("Neutral, CMF and SMA50 Alignment, "
                 "The CMF is aligning with the SMA50, suggesting a balance between short-term and medium-term momentum. "
                 "Action: Adopt a wait-and-see approach. Monitor for potential breakout or breakdown signals and corroborate with other technical indicators."), axis=1)

            df['CMF_Overbought_Oversold_Desc'] = df.apply(
                lambda x:
                ("Sell, Overbought CMF Detected, "
                 "The CMF has reached overbought levels, indicating that the asset might be trading at a premium relative to its intrinsic value. "
                 "Historically, assets in this state might experience pullbacks. Action: Tighten stop-loss orders, consider taking profits, or reducing long positions. Always validate with other technical indicators.")
                if x['CMF_Overbought_Flag']
                else
                ("Buy, Oversold CMF Detected, "
                 "The CMF has entered the oversold territory, suggesting the asset might be undervalued. "
                 "Historically, this can be a buying opportunity, especially if the fundamentals of the asset are strong. Action: Look for potential buying opportunities but ensure confirmation from other indicators and fundamental analysis.")
                if x['CMF_Oversold_Flag']
                else
                ("Neutral, CMF in Normal Range, "
                 "The CMF is neither in an overbought nor oversold state, indicating balanced buying and selling pressures. "
                 "Action: Monitor for potential shifts in momentum, and corroborate with other technical indicators for a clearer market perspective."), axis=1)

            df['CMF_Divergence_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Divergence Detected, "
                 "The Chaikin Money Flow (CMF) shows a bullish divergence when compared to the asset's price. This suggests that while the price is making new lows, the CMF isn't, indicating potential weakening of the bearish momentum. "
                 "Historically, this can precede an upward price movement. Action: Consider potential long positions, but always ensure confirmation from other technical indicators and set a stop-loss.")
                if x['CMF_Bullish_Divergence_Flag']
                else
                ("Sell, Bearish Divergence Detected, "
                 "The CMF displays a bearish divergence relative to the asset's price. This implies that even though the price is achieving new highs, the CMF isn't, hinting at a possible decrease in bullish momentum. "
                 "Historically, this might foreshadow a downward price movement. Action: Exercise caution with long positions, consider taking profits, and set a tighter stop-loss. It's crucial to confirm this with other technical indicators.")
                if x['CMF_Bearish_Divergence_Flag']
                else
                ("Neutral, No Significant Divergence, "
                 "The CMF and the asset's price are moving without showing significant divergence, indicating a lack of clear bullish or bearish bias. "
                 "Action: Maintain vigilance, and monitor for future divergences as they can be potent signals."), axis=1)
            # Initialize consolidated recommendation count columns
            df['CMF_Buy_Count'] = 0
            df['CMF_Sell_Count'] = 0
            df['CMF_Neutral_Count'] = 0

            # List of CMF Description Columns
            desc_columns_cmf = ['CMF_Value_Range_Desc',
                                'CMF_Zero_Crossover_Desc',
                                'CMF_SMA_Comparison_Desc',
                                'CMF_Overbought_Oversold_Desc',
                                'CMF_Divergence_Desc']

            # Iterate Over Each Column and aggregate counts
            for column in desc_columns_cmf:
                df['CMF_Buy_Count'] += df[column].str.startswith(
                    "Buy").astype(int)
                df['CMF_Sell_Count'] += df[column].str.startswith(
                    "Sell").astype(int)
                df['CMF_Neutral_Count'] += df[column].str.startswith(
                    "Neutral").astype(int)

            self.cmf_calculated_signal.emit(df)

        except Exception as e:
            self.logger.log_or_print(
                f"An error occurred in calculate_cmf: {str(e)}", level="ERROR", exc_info=True)
            self.cmf_calculated_signal.emit(df)

    def calculate_macd(self, df, short_period=12, long_period=26, signal_period=9):
        try:
            if df is None:

                self.macd_calculated_signal.emit(None)
                return

            # Compute MACD using pandas-ta
            macd_df = ta.macd(df['Close'], fast=short_period,
                              slow=long_period, signal=signal_period)

            # Extracting MACD, Signal Line, and Histogram from the computed DataFrame
            df['MACD_12_26_9'] = macd_df[f'MACD_{short_period}_{long_period}_{signal_period}'].round(
                2)
            df['MACDs_12_26_9'] = macd_df[f'MACDs_{short_period}_{long_period}_{signal_period}'].round(
                2)
            df['MACDh_12_26_9'] = macd_df[f'MACDh_{short_period}_{long_period}_{signal_period}'].round(
                2)

            # 1. MACD Line and Signal Line Crossover Flags
            df[f'MACD_Bullish_Crossover_Flag'] = df['MACD_12_26_9'] > df['MACDs_12_26_9']
            df[f'MACD_Bearish_Crossover_Flag'] = df['MACD_12_26_9'] < df['MACDs_12_26_9']

            # 2. MACD and the Zero Line Flags
            df[f'MACD_Above_Zero_Flag'] = df['MACD_12_26_9'] > 0
            df[f'MACD_Below_Zero_Flag'] = df['MACD_12_26_9'] < 0

            # 3. MACD Divergence Flags (requires additional logic, placeholder for now)
            df[f'MACD_Bullish_Divergence_Flag'] = False
            df[f'MACD_Bearish_Divergence_Flag'] = False

            # 4. MACD Histogram Flag (positive or negative histogram)
            df[f'MACD_Histogram_Positive_Flag'] = df['MACDh_12_26_9'] > 0
            df[f'MACD_Histogram_Negative_Flag'] = df['MACDh_12_26_9'] < 0

            # 5. MACD Histogram Reversals Flags
            df[f'MACD_Histogram_Reversal_Positive_Flag'] = (
                df['MACDh_12_26_9'] > 0) & (df['MACDh_12_26_9'].shift(1) < 0)
            df[f'MACD_Histogram_Reversal_Negative_Flag'] = (
                df['MACDh_12_26_9'] < 0) & (df['MACDh_12_26_9'].shift(1) > 0)

            # 6. MACD Trend & Double Crossover Flags
            df[f'MACD_Trending_Up_Flag'] = df['MACD_12_26_9'] > df['MACD_12_26_9'].shift(
                1)
            df[f'MACD_Trending_Down_Flag'] = df['MACD_12_26_9'] < df['MACD_12_26_9'].shift(
                1)
            # 1. MACD Line and Signal Line Crossover Interpretation
            df[f'MACD_Crossover_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish Crossover Detected, "
                 "The MACD line has crossed above the Signal line, indicating a potential change in momentum from bearish to bullish. "
                 "Historically, when this crossover occurs after an extended downtrend, it's often interpreted as the early stages of a bullish phase. Action: Consider this as a buying opportunity, but always confirm with other technical indicators and set a stop-loss to protect your position.")
                if x[f'MACD_Bullish_Crossover_Flag']
                else
                ("Sell, Bearish Crossover Detected, "
                 "The MACD line has crossed below the Signal line, suggesting the potential onset of bearish momentum. "
                 "Historically, such a crossover might foreshadow a decline in the asset's price. Action: Consider this as a warning to possibly reduce your holdings, or even open a short position, but always validate with other technical indicators and set a stop-loss.")
                if x[f'MACD_Bearish_Crossover_Flag']
                else
                ("Neutral, No Crossover Detected, "
                 "Currently, there's no significant crossover between the MACD line and the Signal line, suggesting that the asset is moving without a clear bullish or bearish bias. "
                 "Historically, this can be an indication of a period of consolidation or continuation of the current trend. Action: Monitor the asset and wait for clearer signals."), axis=1)

            # 2. MACD and the Zero Line Interpretation
            df[f'MACD_Zero_Line_Desc'] = df.apply(
                lambda x:
                ("Buy, MACD in Bullish Territory, "
                 "The MACD is currently positioned above the zero line. This usually indicates that the asset's short-term momentum is outpacing its long-term momentum. "
                 "Historically, when MACD remains above the zero line for extended periods, it can signal a sustained bullish phase. Action: Consider this as an opportunity to buy or maintain long positions, but always corroborate with other technical and fundamental indicators.")
                if x[f'MACD_Above_Zero_Flag']
                else
                ("Sell, MACD in Bearish Territory, "
                 "The MACD is currently below the zero line, suggesting that the asset's short-term momentum is weaker than its long-term momentum. "
                 "Historically, a MACD position below the zero line can indicate bearish trends or potential downturns. Action: Consider this as a warning to possibly reduce holdings, or even open a short position, but always confirm with other technical indicators and market news.")
                if x[f'MACD_Below_Zero_Flag']
                else
                ("Neutral, MACD Near Zero Line, "
                 "The MACD is oscillating around the zero line, indicating a balance between the asset's short-term and long-term momentum. "
                 "This can suggest a period of market consolidation or a lack of strong momentum in either direction. Action: Monitor the asset for potential breakout patterns or other technical signals."), axis=1)

            # 3. MACD Divergence Interpretation (placeholder logic for the flags)
            df[f'MACD_Divergence_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish MACD Divergence Detected, "
                 "Currently, the asset's price is making new lows while the MACD is not showing the same decline. This discrepancy often suggests potential weakness in the prevailing bearish trend. "
                 "Historically, this kind of divergence has been associated with potential bullish reversals. Action: Consider this as a potential buying opportunity, especially if supported by other bullish indicators, but ensure to set a tight stop-loss.")
                if x[f'MACD_Bullish_Divergence_Flag']
                else
                ("Sell, Bearish MACD Divergence Detected, "
                 "The asset's price is reaching new highs, but the MACD isn't following suit, indicating a potential decline in bullish momentum. "
                 "Historically, this pattern has been a precursor to potential bearish reversals. Action: Exercise caution with current long positions, consider taking profits, and set a trailing stop. It's essential to confirm this divergence with other technical indicators before making decisions.")
                if x[f'MACD_Bearish_Divergence_Flag']
                else
                ("Neutral, No MACD Divergence, "
                 "The MACD and the asset's price are moving in tandem, indicating a consistent trend without any detected divergence. "
                 "This usually suggests that the current trend, whether bullish or bearish, might continue. Action: Monitor the asset for changes in momentum or other confirming technical signals."), axis=1)

            # 4. MACD Histogram Interpretation
            df[f'MACD_Histogram_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish MACD Histogram Detected, "
                 "The MACD histogram is currently positive, indicating that the MACD line is above the Signal line. This is a sign of strong bullish momentum. "
                 "Historically, a positive MACD histogram has been associated with upward trends in the asset's price. Action: Consider holding or even increasing long positions, but remain vigilant for potential signs of a reversal.")
                if x[f'MACD_Histogram_Positive_Flag']
                else
                ("Sell, Bearish MACD Histogram Detected, "
                 "The MACD histogram is currently negative, signaling that the MACD line is below the Signal line. This suggests dominant bearish momentum. "
                 "Historically, a negative MACD histogram has often been an indication of downward trends in the asset's price. Action: It might be a good time to reassess current positions, think about hedging, or even reducing exposure to the asset.")
                if x[f'MACD_Histogram_Negative_Flag']
                else
                ("Neutral, Balanced MACD Histogram, "
                 "The MACD histogram is hovering near zero, which indicates a balance or equilibrium between bullish and bearish forces. "
                 "In such scenarios, the asset's price often moves in a sideways pattern without clear direction. Action: It's advisable to monitor the asset closely, looking for breakout signals or other technical patterns to gauge future movements."), axis=1)

            # 5. MACD Histogram Reversals Interpretation
            df[f'MACD_Histogram_Reversal_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish MACD Histogram Reversal Detected, "
                 "The MACD histogram has recently shifted from negative to positive. This transition is typically viewed as an early sign of potential bullish momentum reversal. "
                 "Historically, such transitions in the MACD histogram have been precursors to upward trends in the asset's price. Action: Be prepared to capitalize on potential uptrends, but always corroborate with other technical indicators before committing to a buying decision.")
                if x[f'MACD_Histogram_Reversal_Positive_Flag']
                else
                ("Sell, Bearish MACD Histogram Reversal Detected, "
                 "The MACD histogram has transitioned from positive to negative. This shift is often seen as an early indication of a potential bearish momentum reversal. "
                 "Historically, a transition like this in the MACD histogram has signaled downward trends in the asset's price. Action: It might be prudent to consider taking protective measures, such as hedging or even selling the asset.")
                if x[f'MACD_Histogram_Reversal_Negative_Flag']
                else
                ("Neutral, No MACD Histogram Reversal Observed, "
                 "Currently, the MACD histogram hasn't shown any significant reversal from its previous trend. "
                 "Without a clear reversal signal, the asset might continue its current trend, whether it's bullish or bearish. Action: It's advisable to continue monitoring the asset and await clearer signals or patterns before making any trading decisions."), axis=1)

            # 6. MACD Trend Interpretation
            df[f'MACD_Trend_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish MACD Trend Detected, "
                 "The MACD line is currently trending upwards, which is often interpreted as increasing bullish momentum. "
                 "Historically, an upward-trending MACD line has been indicative of sustained price increases in the asset. Action: It's advisable to consider staying invested or looking for entry points, while also being vigilant for potential trend reversals.")
                if x[f'MACD_Trending_Up_Flag']
                else
                ("Sell, Bearish MACD Trend Detected, "
                 "The MACD line is trending downwards, suggesting a dominant bearish momentum. "
                 "Historically, a downward-trending MACD line has been a sign of prolonged price declines. Action: Adopt a defensive stance, consider reducing exposure to the asset, or even contemplate shorting opportunities.")
                if x[f'MACD_Trending_Down_Flag']
                else
                ("Neutral, No MACD Trend Observed, "
                 "The MACD line is currently moving sideways or is relatively flat, indicating a potential consolidation phase or a lack of strong momentum in either the bullish or bearish direction. "
                 "Action: It might be wise to adopt a wait-and-see approach, monitoring the asset for potential breakout patterns or signals."), axis=1)
            # Initialize consolidated recommendation count columns for MACD
            df['MACD_Buy_Count'] = 0
            df['MACD_Sell_Count'] = 0
            df['MACD_Neutral_Count'] = 0

            # List of MACD Description Columns
            desc_columns_macd = [f'MACD_Crossover_Desc',
                                 f'MACD_Zero_Line_Desc',
                                 f'MACD_Divergence_Desc',
                                 f'MACD_Histogram_Desc',
                                 f'MACD_Histogram_Reversal_Desc',
                                 f'MACD_Trend_Desc']

            # Iterate Over Each Column and aggregate counts
            for column in desc_columns_macd:
                df['MACD_Buy_Count'] += df[column].str.startswith(
                    "Buy").astype(int)
                df['MACD_Sell_Count'] += df[column].str.startswith(
                    "Sell").astype(int)
                df['MACD_Neutral_Count'] += df[column].str.startswith(
                    "Neutral").astype(int)

            # Assuming you have a signal for MACD like for stochastic
            self.macd_calculated_signal.emit(df)

        except Exception as e:
            self.logger.log_or_print(
                f"An error occurred in calculate_macd: {str(e)}", level="ERROR", exc_info=True)
            # Assuming you have a signal for MACD like for stochastic
            self.macd_calculated_signal.emit(df)

    def calculate_obv(self, df):
        try:
            if df is None:

                self.obv_calculated_signal.emit(None)
                return

            # Rename column for OBV calculation
            df_temp = df.rename(columns={'T.Shares': 'Volume'})

            # Calculate OBV using pandas-ta with renamed DataFrame
            df['OBV'] = df_temp.ta.obv()

            # OBV Value
            df['OBV_Increasing_Flag'] = df['OBV'].diff() > 0
            df['OBV_Decreasing_Flag'] = df['OBV'].diff() < 0
            df['OBV_Value_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish OBV Value Detected, "
                 "The OBV is currently increasing, suggesting that volume is favoring upward price movement. "
                 "Historically, an increasing OBV has been indicative of potential upward price momentum. Action: Consider potential long positions or holding onto current ones.")
                if x['OBV_Increasing_Flag']
                else
                ("Sell, Bearish OBV Value Detected, "
                 "The OBV is currently decreasing, indicating that volume is favoring downward price movement. "
                 "Historically, a decreasing OBV often signals potential downward price momentum. Action: Consider potential short positions or taking profits.")
                if x['OBV_Decreasing_Flag']
                else
                ("Neutral, Stable OBV Value, "
                 "The OBV is relatively stable, suggesting a balance between buying and selling pressures. "
                 "Action: Maintain a balanced approach and monitor the asset for potential signals."),
                axis=1
            )

            # OBV Trend Analysis
            df['OBV_SMA'] = df['OBV'].rolling(window=20).mean()
            df['OBV_above_SMA_Flag'] = df['OBV'] > df['OBV_SMA']
            df['OBV_below_SMA_Flag'] = df['OBV'] < df['OBV_SMA']
            df['OBV_Trend_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish OBV Trend Detected, "
                 "OBV is above its SMA, suggesting positive volume momentum. "
                 "Historically, when OBV is above its SMA, it indicates a potential bullish sentiment. Action: Consider buying opportunities or holding current longs.")
                if x['OBV_above_SMA_Flag']
                else
                ("Sell, Bearish OBV Trend Detected, "
                 "OBV is below its SMA, indicating negative volume momentum. "
                 "Historically, when OBV is below its SMA, it suggests a potential bearish sentiment. Action: Consider selling opportunities or reducing exposure.")
                if x['OBV_below_SMA_Flag']
                else
                ("Neutral, OBV Trending Sideways, "
                 "OBV is around its SMA, indicating no clear trend. "
                 "Action: It might be wise to adopt a wait-and-see approach, monitoring the asset for potential breakout or breakdown patterns."),
                axis=1
            )

            # OBV Rate of Change and Threshold
            df['OBV_RoC'] = df['OBV'].pct_change()
            df['OBV_Surge_Flag'] = df['OBV_RoC'] > 0.05
            df['OBV_Plunge_Flag'] = df['OBV_RoC'] < -0.05
            df['OBV_RoC_Desc'] = df.apply(
                lambda x:
                ("Buy, Significant OBV Surge Detected, "
                 "The rate of change in OBV indicates a strong surge in buying momentum. "
                 "Historically, such surges often correlate with bullish market movements. Action: Consider buying opportunities, but remain vigilant for potential overbought conditions.")
                if x['OBV_Surge_Flag']
                else
                ("Sell, Significant OBV Plunge Detected, "
                 "The rate of change in OBV indicates a strong plunge, suggesting dominant selling momentum. "
                 "Such plunges typically correlate with bearish market phases. Action: Consider selling or shorting opportunities, and be cautious of potential oversold conditions.")
                if x['OBV_Plunge_Flag']
                else
                ("Neutral, Stable OBV Momentum, "
                 "The rate of change in OBV is moderate, indicating neither strong buying nor selling momentum. "
                 "Action: Maintain current positions and monitor for emerging trends."),
                axis=1
            )

            # Divergence Analysis
            df['OBV_Price_Bullish_Divergence_Flag'] = (
                df['Close'].diff() < 0) & (df['OBV'].diff() > 0)
            df['OBV_Price_Bearish_Divergence_Flag'] = (
                df['Close'].diff() > 0) & (df['OBV'].diff() < 0)
            df['OBV_Divergence_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish OBV Divergence Detected, "
                 "While the price is recording new lows, OBV isn't, suggesting potential bullish momentum. "
                 "Historically, bullish divergence is a potential sign of a market turnaround. Action: Consider buying opportunities but validate with other signals before making a decision.")
                if x['OBV_Price_Bullish_Divergence_Flag']
                else
                ("Sell, Bearish OBV Divergence Detected, "
                 "While the price is achieving new highs, OBV isn't keeping pace, suggesting potential bearish momentum. "
                 "Historically, bearish divergence can be an early warning of a price drop. Action: Consider selling or taking profits.")
                if x['OBV_Price_Bearish_Divergence_Flag']
                else
                ("Neutral, No OBV Divergence Observed, "
                 "There's no significant divergence between OBV and price, suggesting the current trend might persist. "
                 "Action: Monitor other indicators and the broader market conditions."),
                axis=1
            )

            # OBV and RSI
            df['OBV_RSI_Bullish_Flag'] = (
                df['OBV'].diff() > 0) & (df['RSI_14'] < 30)
            df['OBV_RSI_Bearish_Flag'] = (
                df['OBV'].diff() < 0) & (df['RSI_14'] > 70)
            df['OBV_RSI_14_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish OBV and RSI Detected, "
                 "OBV is trending upward and RSI is in the oversold territory, suggesting potential bullish momentum. "
                 "Historically, this combination indicates a strong bullish sentiment. Action: Consider buying opportunities and monitor other indicators for confirmation.")
                if x['OBV_RSI_Bullish_Flag']
                else
                ("Sell, Bearish OBV and RSI Detected, "
                 "OBV is trending downward and RSI is in the overbought zone, suggesting potential bearish momentum. "
                 "This combination typically hints at potential selling opportunities. Action: Consider taking profits or shorting opportunities.")
                if x['OBV_RSI_Bearish_Flag']
                else
                ("Neutral, No Clear Signals from OBV and RSI, "
                 "Neither OBV nor RSI are providing strong buy or sell signals. "
                 "Action: Adopt a wait-and-see approach and monitor other technical signals."),
                axis=1
            )

            # OBV and Stoch
            # Assuming you have a 'Stoch' column representing the %K value of Stochastics
            df['OBV_Stoch_Bullish_Flag'] = (
                df['OBV'].diff() > 0) & (df['STOCHk_9_6_3'] < 20)
            df['OBV_Stoch_Bearish_Flag'] = (
                df['OBV'].diff() < 0) & (df['STOCHk_9_6_3'] > 80)
            df['OBV_Stoch_Desc'] = df.apply(
                lambda x:
                ("Buy, Bullish OBV and Stoch Detected, "
                 "OBV is trending upward and Stochastics indicate a potential upward momentum. "
                 "This combination suggests a bullish market outlook. Action: Consider potential long positions and always cross-check with other technical patterns.")
                if x['OBV_Stoch_Bullish_Flag']
                else
                ("Sell, Bearish OBV and Stoch Detected, "
                 "OBV is on a decline and Stochastics indicate potential downward momentum. "
                 "This combination suggests a bearish market phase. Action: Consider potential selling or shorting opportunities.")
                if x['OBV_Stoch_Bearish_Flag']
                else
                ("Neutral, No Clear Signals from OBV and Stoch, "
                 "OBV and Stochastics are not providing significant bullish or bearish indications. "
                 "Action: Maintain current positions and monitor the market for emerging trends."),
                axis=1
            )

            # Initialize consolidated recommendation count columns for obv
            df['OBV_Buy_Count'] = 0
            df['OBV_Sell_Count'] = 0
            df['OBV_Neutral_Count'] = 0

            # List of MACD Description Columns
            desc_columns_obv = [f'OBV_Value_Desc',
                                f'OBV_Trend_Desc',
                                f'OBV_RoC_Desc',
                                f'OBV_Divergence_Desc',
                                f'OBV_RSI_14_Desc',
                                f'OBV_Stoch_Desc']

            # Iterate Over Each Column and aggregate counts
            for column in desc_columns_obv:
                df['OBV_Buy_Count'] += df[column].str.startswith(
                    "Buy").astype(int)
                df['OBV_Sell_Count'] += df[column].str.startswith(
                    "Sell").astype(int)
                df['OBV_Neutral_Count'] += df[column].str.startswith(
                    "Neutral").astype(int)

            self.obv_calculated_signal.emit(df)

        except Exception as e:
            self.logger.log_or_print(
                f"An error occurred in calculate_obv: {str(e)}", level="ERROR")
            self.obv_calculated_signal.emit(df)
