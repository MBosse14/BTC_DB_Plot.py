#Used SQLite and Pandas to make a database and manipulate data for charting

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
from matplotlib import style

style.use('fivethirtyeight')

def build_ohlc(t,o,h,l,c):
	t = mdates.date2num(t)
	return [t,o,h,l,c]

#Chunking
def populate_DB():
	chunks = pd.read_csv('btceUSD.csv', chunksize=400000)
	for chunk in chunks:
		chunk.columns = ['Unix', 'Price', 'Volume']
		with sqlite3.connect('BTC2.db') as conn:
			chunk.to_sql('Bitcoin', conn, if_exists ='append')

#Used to populate the database, commented out after DB was populated
#if running twice		
populate_DB()

#reading from the database
def pull_from_DB():
	with sqlite3.connect('BTC2.db') as conn:
		df = pd.read_sql('SELECT * FROM Bitcoin LIMIT 100000', 
		con=conn, index_col="index")
		
	return df
df = pull_from_DB()
#print(df.head())

#The code below is used to manipulate the data

#Convert to a pandas datetime format from unix, set index to Date
df['Date'] = pd.to_datetime(df['Unix'], unit = 's')
df.set_index('Date', inplace=True)
del(df['Unix'])
print(df.head())

#Resample to open/high/low/close data
ohlc = df['Price'].resample('1D').ohlc()
print(ohlc.tail())

fig = plt.figure()
ax1 = plt.subplot2grid((1,1), (0,0))

#Add a new column for later use, make rolling averages for the plot
ohlc['candlestick_plot'] = list(map(build_ohlc, ohlc.index, ohlc['open'],
ohlc['high'],ohlc['low'],ohlc['close']))
ohlc['10MA'] = ohlc['close'].rolling(10).mean()
ohlc['50MA'] = ohlc['close'].rolling(50).mean()

print(ohlc.tail())

#Plotting the OHLC info with candlestick
candlestick_ohlc(ax1, ohlc['candlestick_plot'])
ohlc['10MA'].plot(ax=ax1, label ='10MA')
ohlc['50MA'].plot(ax=ax1, label ='50MA')

#Pandas gave me to time but if it didn't I would use the code below, also adds tick labels
#ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#for label in ax1.xaxis.get_ticklabels():
	#label.set_rotation(45)

plt.legend(loc=4)

plt.show()









