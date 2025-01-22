import yfinance as yf

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

data = yf.download(symbols, start="2021-01-01", end="2024-12-30")
print(data)
