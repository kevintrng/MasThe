# MasThe
## Master Thesis: Gamified Stock Markets, Sentiment & Volatility
### Diploma Thesis Code Repository

WARNING: The interaction with the Reddit API requires setup of web application by the user, i.e. code cannot be used out of the box!!


NOTE: The `Textmine.ipynb` Jupyter Notebook contains preliminary whole sample textual analysis, including most frequent word, tokens, porter's stems, lemmas, bigrams and most mentioned tickers alongside GME. Graphs in the thesis are produced in the notebook.

 - `findata.py`: Automated script for downloading intraday data and weekly option chains
 - `fivemin.py`: Automated script for downloading monthly 5-minute interval intraday data
 - `gmefun.py`: Script containing all necessary functions interacting with Reddit API thru praw and psaw modules
 - `threads.py`: Script for updating megathreads, dailythreads and number of mentions per month in csv files
 - `wsb_submissions.py`: Script scrapes _r/wallstreetebets_ submissions going over individual months scrapes all submissions found using GME related keywords. Data are saved in the format `submissions_%b`.
 
 
## Data Description
 
 - `gme_dailythreads.csv` and `gme_dailythreads_2020.csv`: contain data on scraped _r/wallstreetbets_ GENERAL daily discussion threads
 - `gme_megathreads.csv`: Large discussion threads related to GME creating during most active periods
 - `postcounter.csv`: Scraping number of posts only from various finance subreddits
 - `submissions_\%b`: Specific posts on WSB related to GME 
 - `intraday`: intraday data (DEPRECIATED due to non-continuity)
 - `fivemin`: five-minute intraday data for sample of stocks (missing data)
 - `EQT.xlsx`: excel file containing Bloomberg downloaded data
 	- 30-min intraday data
	- Historical and Implied Volatility
	- News Sentiment Series
	- Twitter Sentiment Series for GME
- `options`: option chain data manually downloaded each expiry before market open (NOT YET MERGED and most data kept local)
 
