import pandas as pd
from datetime import datetime
from app_config import EXCEL_ENGINE
from LoggerFunction import Logger
import base64
import os


class FileManager:
    def __init__(self):
        self.logger = Logger()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "TICKERS.csv")
        try:
            self.df_tickers = pd.read_csv(csv_path)
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"Initialization: Failed to load CSV. Details: {str(e)}.",
                    level="ERROR",
                    module="TickerLookup",
                )
            raise e

    def save_data_to_excel(self, df, ticker):
        """Save data to Excel file."""
        try:
            if self.logger:
                self.logger.log_or_print(
                    "save_data_to_excel: Method invoked.",
                    level="INFO",
                    module="FileManager",
                )

            if df is not None:
                if self.logger:
                    self.logger.log_or_print(
                        "save_data_to_excel: DataFrame is not None.",
                        level="INFO",
                        module="FileManager",
                    )

                # Get the current datetime
                now = datetime.now()

                # Format the datetime and combine with the ticker name to form the filename
                filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}.xlsx"

                with pd.ExcelWriter(filename, engine=EXCEL_ENGINE) as writer:
                    df.to_excel(writer, sheet_name="Sheet1", index=False)

                if self.logger:
                    self.logger.log_or_print(
                        "Data successfully written to Excel.",
                        level="INFO",
                        module="FileManager",
                    )

                return True
            else:
                if self.logger:
                    self.logger.log_or_print(
                        "save_data_to_excel: DataFrame is None. No data to save.",
                        level="ERROR",
                        module="FileManager",
                    )
                return False
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"save_data_to_excel: An exception occurred. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return False

    def _bool_to_symbol(self, value):
        if value:
            return "✔"  # Checkmark for True
        else:
            return "❌"  # Cross mark for False

    def file_to_base64(self, file_path):
        try:
            with open(file_path, "rb") as file:
                encoded_file = base64.b64encode(file.read())
            return encoded_file.decode("utf-8")
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"file_to_base64: An exception occurred while encoding {file_path}. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return None

    def image_to_base64(self, img_path):
        try:
            return "data:image/png;base64," + self.file_to_base64(img_path)
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"image_to_base64: An exception occurred while converting image {img_path} to base64. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return None

    def css_to_base64(self, css_path):
        try:
            with open(css_path, "r") as file:
                css_content = file.read()
            return "<style>" + css_content + "</style>"
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"css_to_base64: An exception occurred while converting css file {css_path}. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return None

    def embed_css_and_images_in_html(self, html_content, css_path, img_path):
        try:
            base64_css = self.css_to_base64(css_path)
            base64_img = self.image_to_base64(img_path)

            if base64_css and base64_img:
                # Replace CSS link with embedded Base64 CSS
                html_content = html_content.replace(
                    '<link href="report_style.css" rel="stylesheet" />', base64_css
                )

                # Replace image src with Base64 image data
                html_content = html_content.replace(
                    'src="Logo.png"', f'src="{base64_img}"'
                )

                return html_content
            else:
                raise ValueError("Failed to embed CSS or Images.")
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"embed_css_and_images_in_html: An exception occurred. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return None

    def embed_js_in_html(self, html_content, js_path):
        try:
            with open(js_path, "r") as file:
                js_content = file.read()

            js_filename = os.path.basename(js_path)
            embedded_js = f"<script>{js_content}</script>"
            html_content = html_content.replace(
                f'<script src="{js_filename}"></script>', embedded_js
            )

            return html_content
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"embed_js_in_html: An exception occurred while embedding JS file {js_path}. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return None

    def generate_report(self, df, ticker):
        """
        Logic to generate and save the report based on the provided structure.
        """
        try:

            if df is not None:

                # Extract the first 10 columns for standard candle chart
                subset_df = df.iloc[:, :10]
                html_table = subset_df.to_html(
                    classes="styled-table", index=False)
                # Extract the requried columns for SMA anlaysis
                subset_df_sma = df.loc[
                    :,
                    [
                        "Date",
                        "Close",
                        "Open",
                        "High",
                        "Low",
                        "T.Shares",
                        "SMA10",
                        "SMA50",
                        "SMA200",
                    ],
                ]
                html_table_sma = subset_df_sma.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for rsi_9 anlaysis
                subset_df_rsi_9 = df.loc[
                    :, ["Date", "Close", "Open", "High", "Low", "T.Shares", "RSI_9"]
                ]
                html_table_rsi_9 = subset_df_rsi_9.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for rsi_14 anlaysis
                subset_df_rsi_14 = df.loc[
                    :, ["Date", "Close", "Open", "High", "Low", "T.Shares", "RSI_14"]
                ]
                html_table_rsi_14 = subset_df_rsi_14.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for rsi_25 anlaysis
                subset_df_rsi_25 = df.loc[
                    :, ["Date", "Close", "Open", "High", "Low", "T.Shares", "RSI_25"]
                ]
                html_table_rsi_25 = subset_df_rsi_25.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for stoch_9_6_3 anlaysis
                subset_df_stoch_9_6_3 = df.loc[
                    :,
                    [
                        "Date",
                        "Close",
                        "Open",
                        "High",
                        "Low",
                        "T.Shares",
                        "STOCHk_9_6_3",
                        "STOCHd_9_6_3",
                    ],
                ]
                html_table_stoch_9_6_3 = subset_df_stoch_9_6_3.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for cmf_20 anlaysis
                subset_df_cmf_20 = df.loc[
                    :, ["Date", "Close", "Open", "High", "Low", "T.Shares", "CMF_20"]
                ]
                html_table_cmf_20 = subset_df_cmf_20.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for macd_12_26_9 anlaysis
                subset_df_macd_12_26_9 = df.loc[
                    :,
                    [
                        "Date",
                        "Close",
                        "Open",
                        "High",
                        "Low",
                        "T.Shares",
                        "MACD_12_26_9",
                        "MACDs_12_26_9",
                        "MACDh_12_26_9",
                    ],
                ]
                html_table_macd_12_26_9 = subset_df_macd_12_26_9.to_html(
                    classes="styled-table", index=False
                )
                # Extract the requried columns for ovb anlaysis
                subset_df_obv = df.loc[
                    :,
                    [
                        "Date",
                        "Close",
                        "Open",
                        "High",
                        "Low",
                        "T.Shares",
                        "OBV",
                        "OBV_SMA",
                    ],
                ]
                html_table_obv = subset_df_obv.to_html(
                    classes="styled-table", index=False
                )
                # Load the HTML template
                template_path = os.path.join(
                    os.path.dirname(__file__), "report_template.html"
                )
                with open(template_path, "r") as file:
                    template = file.read()

                # Fetch the last row of the DataFrame
                last_row = df.iloc[-1]
                # get company name from ticker
                company_name = self.get_company_name(ticker)
                # Replace placeholders in the main template
                now = datetime.now()
                formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
                replacements = {
                    "table": html_table,
                    "table_sma": html_table_sma,
                    "table_rsi_9": html_table_rsi_9,
                    "table_rsi_14": html_table_rsi_14,
                    "table_rsi_25": html_table_rsi_25,
                    "table_stoch_9_6_3": html_table_stoch_9_6_3,
                    "table_cmf_20": html_table_cmf_20,
                    "table_macd_12_26_9": html_table_macd_12_26_9,
                    "table_obv": html_table_obv,
                    "ticker_name": ticker,
                    "company_name": company_name,
                    "report_date": formatted_date,
                    "sma10_value": last_row["SMA10"],
                    "sma50_value": last_row["SMA50"],
                    "sma200_value": last_row["SMA200"],
                    "golden_cross_flag": self._bool_to_symbol(last_row["Golden_Cross"]),
                    "death_cross_flag": self._bool_to_symbol(last_row["Death_Cross"]),
                    "price_cross_sma10_up_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA10_Up"]
                    ),
                    "price_cross_sma10_down_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA10_Down"]
                    ),
                    "price_cross_sma50_up_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA50_Up"]
                    ),
                    "price_cross_sma50_down_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA50_Down"]
                    ),
                    "price_cross_sma200_up_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA200_Up"]
                    ),
                    "price_cross_sma200_down_flag": self._bool_to_symbol(
                        last_row["Price_Cross_SMA200_Down"]
                    ),
                    "sma10_cross_sma200_up_flag": self._bool_to_symbol(
                        last_row["SMA10_Cross_SMA200_Up"]
                    ),
                    "sma10_cross_sma200_down_flag": self._bool_to_symbol(
                        last_row["SMA10_Cross_SMA200_Down"]
                    ),
                    "sma10_up_flag": self._bool_to_symbol(last_row["SMA10_Up"]),
                    "sma50_up_flag": self._bool_to_symbol(last_row["SMA50_Up"]),
                    "sma200_up_flag": self._bool_to_symbol(last_row["SMA200_Up"]),
                    "golden_death_cross_desc": last_row["Golden_Death_Cross_Desc"],
                    "price_sma10_crossover_desc": last_row[
                        "Price_SMA10_Crossover_Desc"
                    ],
                    "price_crossover_desc": last_row["Price_Crossover_Desc"],
                    "price_sma200_crossover_desc": last_row[
                        "Price_SMA200_Crossover_Desc"
                    ],
                    "sma10_sma200_crossover_desc": last_row[
                        "SMA10_SMA200_Crossover_Desc"
                    ],
                    "sma_slopes_desc": last_row["SMA_Slopes_Desc"],
                    "price_distance_sma10_desc": last_row["Price_Distance_SMA10_Desc"],
                    "price_distance_sma50_desc": last_row["Price_Distance_SMA50_Desc"],
                    "price_distance_sma200_desc": last_row[
                        "Price_Distance_SMA200_Desc"
                    ],
                    "sma_relationship_10_50_desc": last_row[
                        "SMA_Relationship_10_50_Desc"
                    ],
                    "sma_relationship_50_200_desc": last_row[
                        "SMA_Relationship_50_200_Desc"
                    ],
                    "sma10_above_sma50_flag": self._bool_to_symbol(
                        last_row["SMA10_Above_SMA50"]
                    ),
                    "sma50_above_sma200_flag": self._bool_to_symbol(
                        last_row["SMA50_Above_SMA200"]
                    ),
                    "Price_Distance_SMA10": self._bool_to_symbol(
                        last_row["Price_Distance_SMA10"]
                    ),
                    "Price_Distance_SMA50": self._bool_to_symbol(
                        last_row["Price_Distance_SMA50"]
                    ),
                    "Price_Distance_SMA200": self._bool_to_symbol(
                        last_row["Price_Distance_SMA200"]
                    ),
                    "sma_buy_count": last_row["SMA_Buy_Count"],
                    "sma_sell_count": last_row["SMA_Sell_Count"],
                    "sma_neutral_count": last_row["SMA_Neutral_Count"],
                    # Additions for RSI_9
                    "RSI_9": last_row["RSI_9"],
                    "RSI_9_Overbought_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Overbought_Flag"]
                    ),
                    "RSI_9_Oversold_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Oversold_Flag"]
                    ),
                    "RSI_9_Neutral_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Neutral_Flag"]
                    ),
                    "RSI_9_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Bearish_Divergence_Flag"]
                    ),
                    "RSI_9_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Bullish_Divergence_Flag"]
                    ),
                    "RSI_9_Swing_Failure_Buy_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Swing_Failure_Buy_Flag"]
                    ),
                    "RSI_9_Swing_Failure_Sell_Flag": self._bool_to_symbol(
                        last_row["RSI_9_Swing_Failure_Sell_Flag"]
                    ),
                    "RSI_9_Overbought_Oversold_Desc": last_row[
                        "RSI_9_Overbought_Oversold_Desc"
                    ],
                    "RSI_9_Divergence_Desc": last_row["RSI_9_Divergence_Desc"],
                    "RSI_9_Swings_Desc": last_row["RSI_9_Swings_Desc"],
                    "RSI_9_buy_count": last_row["RSI_9_Buy_Count"],
                    "RSI_9_sell_count": last_row["RSI_9_Sell_Count"],
                    "RSI_9_neutral_count": last_row["RSI_9_Neutral_Count"],
                    # Additions for RSI_14
                    "RSI_14": last_row["RSI_14"],
                    "RSI_14_Overbought_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Overbought_Flag"]
                    ),
                    "RSI_14_Oversold_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Oversold_Flag"]
                    ),
                    "RSI_14_Neutral_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Neutral_Flag"]
                    ),
                    "RSI_14_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Bearish_Divergence_Flag"]
                    ),
                    "RSI_14_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Bullish_Divergence_Flag"]
                    ),
                    "RSI_14_Swing_Failure_Buy_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Swing_Failure_Buy_Flag"]
                    ),
                    "RSI_14_Swing_Failure_Sell_Flag": self._bool_to_symbol(
                        last_row["RSI_14_Swing_Failure_Sell_Flag"]
                    ),
                    "RSI_14_Overbought_Oversold_Desc": last_row[
                        "RSI_14_Overbought_Oversold_Desc"
                    ],
                    "RSI_14_Divergence_Desc": last_row["RSI_14_Divergence_Desc"],
                    "RSI_14_Swings_Desc": last_row["RSI_14_Swings_Desc"],
                    "RSI_14_buy_count": last_row["RSI_14_Buy_Count"],
                    "RSI_14_sell_count": last_row["RSI_14_Sell_Count"],
                    "RSI_14_neutral_count": last_row["RSI_14_Neutral_Count"],
                    # Additions for RSI_25
                    "RSI_25": last_row["RSI_25"],
                    "RSI_25_Overbought_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Overbought_Flag"]
                    ),
                    "RSI_25_Oversold_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Oversold_Flag"]
                    ),
                    "RSI_25_Neutral_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Neutral_Flag"]
                    ),
                    "RSI_25_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Bearish_Divergence_Flag"]
                    ),
                    "RSI_25_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Bullish_Divergence_Flag"]
                    ),
                    "RSI_25_Swing_Failure_Buy_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Swing_Failure_Buy_Flag"]
                    ),
                    "RSI_25_Swing_Failure_Sell_Flag": self._bool_to_symbol(
                        last_row["RSI_25_Swing_Failure_Sell_Flag"]
                    ),
                    "RSI_25_Overbought_Oversold_Desc": last_row[
                        "RSI_25_Overbought_Oversold_Desc"
                    ],
                    "RSI_25_Divergence_Desc": last_row["RSI_25_Divergence_Desc"],
                    "RSI_25_Swings_Desc": last_row["RSI_25_Swings_Desc"],
                    "RSI_25_buy_count": last_row["RSI_25_Buy_Count"],
                    "RSI_25_sell_count": last_row["RSI_25_Sell_Count"],
                    "RSI_25_neutral_count": last_row["RSI_25_Neutral_Count"],
                    # Additions for STOCHk_9_6_3
                    "STOCHk_9_6_3": last_row["STOCHk_9_6_3"],
                    "STOCHd_9_6_3": last_row["STOCHd_9_6_3"],
                    "STOCH_9_6_3_Overbought_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Overbought_Flag"]
                    ),
                    "STOCH_9_6_3_Oversold_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Oversold_Flag"]
                    ),
                    "STOCH_9_6_3_Bullish_Crossover_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Bullish_Crossover_Flag"]
                    ),
                    "STOCH_9_6_3_Bearish_Crossover_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Bearish_Crossover_Flag"]
                    ),
                    "STOCH_9_6_3_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Bullish_Divergence_Flag"]
                    ),
                    "STOCH_9_6_3_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Bearish_Divergence_Flag"]
                    ),
                    "STOCH_9_6_3_Midpoint_Cross_Up_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Midpoint_Cross_Up_Flag"]
                    ),
                    "STOCH_9_6_3_Midpoint_Cross_Down_Flag": self._bool_to_symbol(
                        last_row["STOCH_9_6_3_Midpoint_Cross_Down_Flag"]
                    ),
                    "STOCH_9_6_3_Overbought/Oversold_Desc": last_row[
                        "STOCH_9_6_3_Overbought/Oversold_Desc"
                    ],
                    "STOCH_9_6_3_Divergence_Desc": last_row[
                        "STOCH_9_6_3_Divergence_Desc"
                    ],
                    "STOCH_9_6_3_Swings_Desc": last_row["STOCH_9_6_3_Swings_Desc"],
                    "STOCH_9_6_3_buy_count": last_row["STOCH_9_6_3_Buy_Count"],
                    "STOCH_9_6_3_sell_count": last_row["STOCH_9_6_3_Sell_Count"],
                    "STOCH_9_6_3_neutral_count": last_row["STOCH_9_6_3_Neutral_Count"],
                    # Additions for CFM_20
                    "CMF_20": last_row["CMF_20"],
                    "CMF_Positive_Flag": self._bool_to_symbol(
                        last_row["CMF_Positive_Flag"]
                    ),
                    "CMF_Negative_Flag": self._bool_to_symbol(
                        last_row["CMF_Negative_Flag"]
                    ),
                    "CMF_Neutral_Flag": self._bool_to_symbol(
                        last_row["CMF_Neutral_Flag"]
                    ),
                    "CMF_Zero_Crossover_Up_Flag": self._bool_to_symbol(
                        last_row["CMF_Zero_Crossover_Up_Flag"]
                    ),
                    "CMF_Zero_Crossover_Down_Flag": self._bool_to_symbol(
                        last_row["CMF_Zero_Crossover_Down_Flag"]
                    ),
                    "CMF_Above_SMA50_Flag": self._bool_to_symbol(
                        last_row["CMF_Above_SMA50_Flag"]
                    ),
                    "CMF_Below_SMA50_Flag": self._bool_to_symbol(
                        last_row["CMF_Below_SMA50_Flag"]
                    ),
                    "CMF_Overbought_Flag": self._bool_to_symbol(
                        last_row["CMF_Overbought_Flag"]
                    ),
                    "CMF_Oversold_Flag": self._bool_to_symbol(
                        last_row["CMF_Oversold_Flag"]
                    ),
                    "CMF_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["CMF_Bullish_Divergence_Flag"]
                    ),
                    "CMF_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["CMF_Bearish_Divergence_Flag"]
                    ),
                    "CMF_Value_Range_Desc": last_row["CMF_Value_Range_Desc"],
                    "CMF_Zero_Crossover_Desc": last_row["CMF_Zero_Crossover_Desc"],
                    "CMF_SMA_Comparison_Desc": last_row["CMF_SMA_Comparison_Desc"],
                    "CMF_Overbought_Oversold_Desc": last_row[
                        "CMF_Overbought_Oversold_Desc"
                    ],
                    "CMF_Divergence_Desc": last_row["CMF_Divergence_Desc"],
                    "CMF_buy_count": last_row["CMF_Buy_Count"],
                    "CMF_sell_count": last_row["CMF_Sell_Count"],
                    "CMF_neutral_count": last_row["CMF_Neutral_Count"],
                    # Additions for MACD_12_26_9
                    "MACD_12_26_9": last_row["MACD_12_26_9"],
                    "MACDs_12_26_9": last_row["MACDs_12_26_9"],
                    "MACDh_12_26_9": last_row["MACDh_12_26_9"],
                    "MACD_Bullish_Crossover_Flag": self._bool_to_symbol(
                        last_row["MACD_Bullish_Crossover_Flag"]
                    ),
                    "MACD_Bearish_Crossover_Flag": self._bool_to_symbol(
                        last_row["MACD_Bearish_Crossover_Flag"]
                    ),
                    "MACD_Above_Zero_Flag": self._bool_to_symbol(
                        last_row["MACD_Above_Zero_Flag"]
                    ),
                    "MACD_Below_Zero_Flag": self._bool_to_symbol(
                        last_row["MACD_Below_Zero_Flag"]
                    ),
                    "MACD_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["MACD_Bullish_Divergence_Flag"]
                    ),
                    "MACD_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["MACD_Bearish_Divergence_Flag"]
                    ),
                    "MACD_Histogram_Positive_Flag": self._bool_to_symbol(
                        last_row["MACD_Histogram_Positive_Flag"]
                    ),
                    "MACD_Histogram_Negative_Flag": self._bool_to_symbol(
                        last_row["MACD_Histogram_Negative_Flag"]
                    ),
                    "MACD_Histogram_Reversal_Positive_Flag": self._bool_to_symbol(
                        last_row["MACD_Histogram_Reversal_Positive_Flag"]
                    ),
                    "MACD_Histogram_Reversal_Negative_Flag": self._bool_to_symbol(
                        last_row["MACD_Histogram_Reversal_Negative_Flag"]
                    ),
                    "MACD_Trending_Up_Flag": self._bool_to_symbol(
                        last_row["MACD_Trending_Up_Flag"]
                    ),
                    "MACD_Trending_Down_Flag": self._bool_to_symbol(
                        last_row["MACD_Trending_Down_Flag"]
                    ),
                    "MACD_Crossover_Desc": last_row["MACD_Crossover_Desc"],
                    "MACD_Zero_Line_Desc": last_row["MACD_Zero_Line_Desc"],
                    "MACD_Divergence_Desc": last_row["MACD_Divergence_Desc"],
                    "MACD_Histogram_Desc": last_row["MACD_Histogram_Desc"],
                    "MACD_Histogram_Reversal_Desc": last_row[
                        "MACD_Histogram_Reversal_Desc"
                    ],
                    "MACD_Trend_Desc": last_row["MACD_Trend_Desc"],
                    "MACD_buy_count": last_row["MACD_Buy_Count"],
                    "MACD_sell_count": last_row["MACD_Sell_Count"],
                    "MACD_neutral_count": last_row["MACD_Neutral_Count"],
                    # Additions for OBV
                    "OBV": last_row["OBV"],
                    "OBV_SMA": last_row["OBV_SMA"],
                    "OBV_RoC": last_row["OBV_RoC"],
                    "OBV_Increasing_Flag": self._bool_to_symbol(
                        last_row["OBV_Increasing_Flag"]
                    ),
                    "OBV_Decreasing_Flag": self._bool_to_symbol(
                        last_row["OBV_Decreasing_Flag"]
                    ),
                    "OBV_above_SMA_Flag": self._bool_to_symbol(
                        last_row["OBV_above_SMA_Flag"]
                    ),
                    "OBV_below_SMA_Flag": self._bool_to_symbol(
                        last_row["OBV_below_SMA_Flag"]
                    ),
                    "OBV_Surge_Flag": self._bool_to_symbol(last_row["OBV_Surge_Flag"]),
                    "OBV_Plunge_Flag": self._bool_to_symbol(
                        last_row["OBV_Plunge_Flag"]
                    ),
                    "OBV_Price_Bullish_Divergence_Flag": self._bool_to_symbol(
                        last_row["OBV_Price_Bullish_Divergence_Flag"]
                    ),
                    "OBV_Price_Bearish_Divergence_Flag": self._bool_to_symbol(
                        last_row["OBV_Price_Bearish_Divergence_Flag"]
                    ),
                    "OBV_RSI_Bullish_Flag": self._bool_to_symbol(
                        last_row["OBV_RSI_Bullish_Flag"]
                    ),
                    "OBV_RSI_Bearish_Flag": self._bool_to_symbol(
                        last_row["OBV_RSI_Bearish_Flag"]
                    ),
                    "OBV_Stoch_Bullish_Flag": self._bool_to_symbol(
                        last_row["OBV_Stoch_Bullish_Flag"]
                    ),
                    "OBV_Stoch_Bearish_Flag": self._bool_to_symbol(
                        last_row["OBV_Stoch_Bearish_Flag"]
                    ),
                    "OBV_Value_Desc": last_row["OBV_Value_Desc"],
                    "OBV_Trend_Desc": last_row["OBV_Trend_Desc"],
                    "OBV_RoC_Desc": last_row["OBV_RoC_Desc"],
                    "OBV_Divergence_Desc": last_row["OBV_Divergence_Desc"],
                    "OBV_RSI_14_Desc": last_row["OBV_RSI_14_Desc"],
                    "OBV_Stoch_Desc": last_row["OBV_Stoch_Desc"],
                    "OBV_buy_count": last_row["OBV_Buy_Count"],
                    "OBV_sell_count": last_row["OBV_Sell_Count"],
                    "OBV_neutral_count": last_row["OBV_Neutral_Count"],
                    # Total Count for Buys and Sells
                    "total_buy_count": last_row["SMA_Buy_Count"]
                    + last_row["RSI_9_Buy_Count"]
                    + last_row["RSI_14_Buy_Count"]
                    + last_row["RSI_25_Buy_Count"]
                    + last_row["STOCH_9_6_3_Buy_Count"]
                    + last_row["CMF_Buy_Count"]
                    + last_row["MACD_Buy_Count"]
                    + last_row["OBV_Buy_Count"],
                    "total_sell_count": last_row["SMA_Sell_Count"]
                    + last_row["RSI_9_Sell_Count"]
                    + last_row["RSI_14_Sell_Count"]
                    + last_row["RSI_25_Sell_Count"]
                    + last_row["STOCH_9_6_3_Sell_Count"]
                    + last_row["CMF_Sell_Count"]
                    + last_row["MACD_Sell_Count"]
                    + last_row["OBV_Sell_Count"],
                    "total_neutral_count": last_row["SMA_Neutral_Count"]
                    + last_row["RSI_9_Neutral_Count"]
                    + last_row["RSI_14_Neutral_Count"]
                    + last_row["RSI_25_Neutral_Count"]
                    + last_row["STOCH_9_6_3_Neutral_Count"]
                    + last_row["CMF_Neutral_Count"]
                    + last_row["MACD_Neutral_Count"]
                    + last_row["OBV_Neutral_Count"],
                }
                for key, value in replacements.items():
                    template = template.replace(f"{{{key}}}", str(value))

                # Format the datetime and combine with the ticker name to form the filename
                filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}_report.html"

                # Save to an HTML file
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(template)
                try:
                    css_filepath = os.path.join(
                        os.path.dirname(__file__), "report_style.css"
                    )
                    img_filepath = os.path.join(
                        os.path.dirname(__file__), "Logo.png")

                    template = self.embed_css_and_images_in_html(
                        template, css_filepath, img_filepath
                    )
                    # Embedding JS files one-by-one
                    js_files = [
                        "chart_cmf_20.js",
                        "chart_macd_12_26_9.js",
                        "chart_Main.js",
                        "chart_rsi_9.js",
                        "chart_rsi_14.js",
                        "chart_rsi_25.js",
                        "chart_SMA.js",
                        "chart_stoch_9_6_3.js",
                        "chart_obv.js",
                        "collapsible_handler.js",
                    ]

                    for js_file in js_files:
                        template = self.embed_js_in_html(template, js_file)
                    if not template:
                        raise ValueError(
                            "Failed to embed CSS or Images in the report.")
                    # Save the embedded version as a new file
                    embedded_filename = f"{now.strftime('%Y-%m-%d %H-%M-%S')}_{ticker}_report_embedded.html"
                    with open(embedded_filename, "w", encoding="utf-8") as f:
                        f.write(template)
                except Exception as e:
                    if self.logger:
                        self.logger.log_or_print(
                            f"generate_report: An exception occurred while embedding CSS or Images. Details: {str(e)}.",
                            level="ERROR",
                            module="FileManager",
                        )
                    return False

                # Now you should have the MHTML saved in the current directory

                return True
            else:
                if self.logger:
                    self.logger.log_or_print(
                        "generate_report: DataFrame is None. No data to save.",
                        level="ERROR",
                        module="FileManager",
                    )
                return False
        except Exception as e:
            if self.logger:
                self.logger.log_or_print(
                    f"generate_report: An exception occurred. Details: {str(e)}.",
                    level="ERROR",
                    module="FileManager",
                )
            return False

    def get_company_name(self, ticker):
        """
        Retrieves the company name based on the provided ticker.

        :param ticker: The ticker symbol of the company.
        :return: The company name corresponding to the ticker, or an error message if not found.
        """
        try:
            return self.df_tickers[self.df_tickers["Ticker"] == ticker]["Name"].values[
                0
            ]
        except IndexError:
            # Handle case where ticker is not found

            return "Ticker not found in the dataset."
        except Exception as e:
            # Handle other exceptions
            if self.logger:
                self.logger.log_or_print(
                    f"get_company_name: An exception occurred. Details: {str(e)}.",
                    level="ERROR",
                    module="TickerLookup",
                )
            return False


# Example usage:
# lookup = TickerLookup("/path/to/TICKERS.csv", logger)
# company_name = lookup.get_company_name("AAHP")
