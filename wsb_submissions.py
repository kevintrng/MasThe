#!/Users/kevintrng/opt/anaconda3/bin/python3
from gmefun import *
import os
import sys
import prawcore
    
class SubmissionsWSB:
    
    ###Define paths to save files
    dir_path = os.path.dirname(__file__)
    data_path = os.path.join(dir_path,'data')

    ###Get date range
    ##User specified from command line
    if int(sys.argv[1]) != 0:
        month = int(sys.argv[1])
        date_range = (datetime.datetime(2021,month,1), eomday(datetime.datetime(2021,month,1)))
        month_name = date_range[1].strftime('%b').lower()
    else:
        month = datetime.date.today().month
        date_range = (datetime.datetime(2021,month-1,1), eomday(datetime.datetime(2021,month-1,1)))
        month_name = date_range[1].strftime('%b').lower()
    
    def __init__(self):
        ###Initialise objects to be written to
        self.names = ['title', 'id', 'selftext', 'created']
        self.gmequery  = 'GME|GAMESTOP|GameStop|gamestop|Gamestop|$GME|Citadel|Melvin'
        self.gmeposts = []

    def getPosts(self):
        ###Fetch submissions via psaw api
        submissions = api.search_submissions(subreddit = 'wallstreetbets', 
                                             after = self.date_range[0], 
                                             before = self.date_range[1], 
                                             query = self.gmequery,
                                             mod_removed = False, user_removed = False,
                                             limit = None, 
                                             filter = self.names)

        ###Loop through generator get info to dictionary
        for post in tqdm(submissions, desc = 'WSB Submissions', colour = 'green', leave = True):
            self.gmeposts.append([post.title, post.id, post.selftext, post.created])

        ###Save to csv and print success message
        save_path = os.path.join(self.data_path,f'submissions_{self.month_name}.csv')
        pd.DataFrame(self.gmeposts, columns = self.names).to_csv(save_path)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: WSB Submisssions for month {self.month_name.capitalize()} downloaded")

def main():
    download = SubmissionsWSB()
    download.getPosts()

if __name__ == '__main__':
    main()