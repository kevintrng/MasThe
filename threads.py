#!/Users/kevintrng/opt/anaconda3/bin/python3

from gmefun import *
import prawcore
import os

import concurrent.futures

class Threads:
    
    ###Setup paths and today's date
    dir_path = os.path.dirname(__file__)
    data_path = os.path.join(dir_path,'data')
    dt_today = datetime.date.today()
    
    def __init__(self):
        self.start_date = None
        self.path = None
        self.data = None
    
    ###Update megathreads
    def getMegathreads(self, csv):
        self.path = os.path.join(self.data_path,csv)
        self.data = pd.read_csv(self.path, index_col = 0, parse_dates = ['datetime']).sort_index()
        self.start_date = self.data.datetime.max()
        
        ###Using reddit global variable fetch GME megathreads
        megathreads = psaw_getPosts(reddit,'wallstreetbets','GME Megathread', afterdate = self.start_date,
                                    beforedate = self.dt_today, lmt = 1000, lmt_comms = 100)
        megathreads['datetime'] = [datetime.datetime.utcfromtimestamp(dt) for dt in megathreads["created"]]
        self.data = pd.concat([self.data, megathreads], ignore_index = True)
        
        ###Save the updated csv file
        self.data.to_csv(os.path.join(self.data_path, csv))
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Megathreads Updated {megathreads.shape[0]} rows added")
    
    ###Update dailythreads
    def getDailyThreads(self, csv):
        self.path = os.path.join(self.data_path, csv)
        self.data = pd.read_csv(self.path, index_col = 0, parse_dates = ['datetime'])
        self.start_date = self.data.datetime.max()
        
        if self.start_date.date() == self.dt_today-datetime.timedelta(days=1):
            return print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: DailyThreads up to date!")
        else:
            ###Fetch newest dailythreads from last recorded date
            dailythreads = getThreadsbyFlair(reddit, "wallstreetbets", "Daily Discussion Thread", "Daily Discussion",
                                             self.start_date, self.dt_today, lmt = 1000)

            ###Transform datetime column from utc timestamp to datetime format
            dailythreads['datetime'] = [datetime.datetime.utcfromtimestamp(dt) for dt in dailythreads["created"]]

            ###Go through dailythreads and fetch mentions up to 1000 comments for each thread
            mentions = []
            keywords = ['GME','gme','Gamestop','GameStop','gamestop','GAMESTOP','$GME']
            
            ###Helper function to be used in threading
            def Mentions(dailythread):
                try:
                    mentions.append(getNumberOfMentions(dailythread, keywords, lmt = 1000, depth = 5))
                except prawcore.exceptions.TooLarge:
                    mentions.append(getNumberOfMentions(dailythread, keywords, lmt = 1000, depth = 0))
            ###Multithreading calls to each dailythread using map
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(Mentions, dailythreads.id), total = len(dailythreads.id)))
            
            ###WARNING: Multithreading may results in inordered entries with respect to date!
            ###Merge dataframes and mentions
            dailythreads = pd.concat([dailythreads,pd.DataFrame(mentions)], axis = 1)
            ###Compute percentage of mentions
            dailythreads['pct_mention'] = dailythreads['NumberOfMentions']/dailythreads['NumberOfComments']
            
            ###Update dataframe
            ##Sort values via datetime and reset index to correct mismatch in entries
            self.data = pd.concat([self.data, dailythreads], ignore_index = True).sort_values('datetime').reset_index(drop = True)
            self.data.to_csv(os.path.join(self.data_path, csv))

            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Dailythreads Updated {dailythreads.shape[0]} rows added")

    ###Updates postocunter (individual subreddit mentions)
    def getSubredditMentions(self, csv):
        ###Overall Subreddit Post Mentions
        self.path = os.path.join(self.data_path, csv)
        self.data = pd.read_csv(self.path, index_col = 'subreddit', parse_dates=['date'],
                                date_parser=lambda x: datetime.datetime.strptime(x, "%b%y"))
        self.start_date = self.data.date.max()
        
        if self.start_date.month+1 == self.dt_today.month:
            return print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Subreddit mentions up to date (until month {self.start_date.month})")
        
        ###Get monthly ranges organized in list of tuples (start_of_month, end_of_month)
        from_to_list = [(datetime.datetime(2021,i,1),
                         eomday(datetime.datetime(2021,i,1)))
                        for i in range(self.start_date.month+1,self.dt_today.month)]
        ###Set up date index in format bbyy
        dt_idx = [datetime.datetime.strftime(tup[0],"%b%y") for tup in from_to_list]
        
        ###Get subreddits to search
        subreddits = self.data.index.unique().tolist()
        query  = 'GME|GAMESTOP|GameStop|gamestop|Gamestop|$GME|Citadel|Melvin'
        post_counter = {sub:[] for sub in subreddits}

        ###Helper function for MULTITHREADING
        ###Loop through subreddits and then date_ranges(organized in tuples)
        for sub in tqdm(subreddits, desc = 'SubLoop', colour = 'green'):
            for start, end in tqdm(from_to_list, desc = 'DateLoop', leave = False, colour = 'green'):
                try:
                    post_counter[sub].append(psaw_counter(api, sub, query,
                                                          afterdate = start, beforedate = end,
                                                          lmt = None, lmt_comms = 100))
                ###If no posts are found append array of zeroes
                except ZeroDivisionError:
                    post_counter[sub].append({i:0 for i in ['found_posts','filtered_posts','pct_filtered']})
        ###Merge list of pandas dataframes indexed by subreddit-date tuples
        post_counter = pd.concat([pd.DataFrame(post_counter[sub], index = dt_idx) for sub in subreddits], keys = subreddits)
        ###Re-transform date column to be saved and set as index
        self.data.date = self.data.date.apply(lambda x: x.strftime("%b%y"))
        self.data.set_index('date', append = True, inplace = True)
        self.data = pd.concat([self.data, post_counter]).sort_index(level = "subreddit", sort_remaining = False)
        self.data.to_csv(os.path.join(self.data_path, csv))
        
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Sub postcounter updated {post_counter.shape[0]} rows added")

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
###Main execution function
def main():
    ###Initialise class
    download = Threads()
    ###Megathreads
    download.getMegathreads('gme_megathreads.csv')
    ###Dailythreads
    download.getDailyThreads('gme_dailythreads.csv')
    ###Subreddit Mentions
    download.getSubredditMentions('postcounter.csv')
    
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
###Script execution
if __name__ == '__main__':
    main()