import yfinance as yf
import psycopg2
import pandas as pd 

symbols = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOG", "GOOGL", "META", "TSLA", "PEP", "AVGO",
    "COST", "CSCO", "ADBE", "NFLX", "CMCSA", "AMD", "QCOM", "INTC", "HON",
    "INTU", "AMGN", "SBUX", "AMAT", "MDLZ", "ADI", "ISRG", "BKNG", "LRCX", "GILD",
    "ADP", "VRTX", "MU", "REGN", "KLAC", "MRVL", "SNPS", "PANW", "CDNS",
    "CSX", "MELI", "MNST", "LULU", "FTNT", "NXPI", "KDP", "ORLY", "MAR",
    "CTAS", "PAYX", "EXC", "ODFL", "TEAM", "XEL", "FAST", "BIIB", "ROST", "CTSH",
    "CHTR", "DLTR", "PCAR", "VRSK", "WBD", "AEP", "IDXX", "MCHP", "AZN", "EA",
    "ANSS", "ALGN", "KHC", "BKR", "CDW", "DDOG", "CPRT", "CRWD", "DXCM",
    "ZS", "CEG", "GFS", "PLTR", "MSTR", "AXON", "LIN", "ARM", "SMCI", "APP",
    "GEHC", "ON", "TTWO", "PDD", "RIVN", "WBA", "ILMN", "LCID", "OKTA", "NTES",
    "BIDU", "DOCU", "MTCH", "VRSN", "TCOM"
]

# Collect all data at once
# Use a list comprehension to download and process data
all_data = [
    yf.download(symbol, start="2021-01-01", end="2024-12-30").assign(Ticker=symbol)
    for symbol in symbols
]

# Concatenate all data into one DataFrame
final_data = pd.concat(all_data, axis=0)

# Reset index for a clean format
final_data.reset_index(inplace=True)

final_data.to_csv("historic_financial_data.csv", index=False)


# #connect to postgreSQL
# conn = psycopg2.connect(
#     dbname="postgres", user="akilfiros", password="", host="127.0.0.1"
# )
# cur = conn.cursor()

# # Insert data
# for index, row in data.iterrows():
#     cur.execute(
#         "INSERT INTO financial_data (date, ticker, close, volume) VALUES (%s, %s, %s, %s)",
#         (row['DATE'], row['Ticker'], row['Close'], row['Volume']),
#     )

# conn.commit()
# cur.close()
# conn.close()


