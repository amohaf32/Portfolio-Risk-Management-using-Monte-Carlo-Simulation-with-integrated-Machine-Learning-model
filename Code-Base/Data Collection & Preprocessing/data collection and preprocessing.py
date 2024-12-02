import numpy as np 
import pandas as pd
import requests

#collectiing histoic data from the alpha vantage api 

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=8M9KQDJPDXRDACRV'
r = requests.get(url)
data = r.json()

print(data)


# import numpy as np 
# import pandas as pd
# import requests

# #collectiing histoic data from the alpha vantage api 

# url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&outputsize=full&apikey=8M9KQDJPDXRDACRV'
# r = requests.get(url)
# data = r.json()

# print(data)