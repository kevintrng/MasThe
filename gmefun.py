import praw
import pandas as pd
import datetime
from psaw import PushshiftAPI
from tqdm import tqdm
from secret import*

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
###GLOBAL VARIABLES SETUP
reddit = praw.Reddit(client_id = user_id, client_secret = user_secret, user_agent = "webtest")
api = PushshiftAPI(reddit)
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

def getNumberOfMentions(submission_id, keywords, lmt = 100, depth = 10):
    submission = reddit.submission(id = submission_id)
    mentions = 0
    submission.comments.replace_more(limit = depth)
    for comms in submission.comments[:lmt]:
        if any(keys in comms.body for keys in keywords):
            mentions += 1
    return {'NumberOfMentions': mentions, 'NumberOfComments': submission.comments[:lmt].__len__()}


def psaw_getPosts(reddit_praw, sub_name, query, afterdate, beforedate, lmt = 100, lmt_comms = 100):
    '''
    reddit_praw = reddit.Praw object (personalised)
    sub_name = Subreddit Name
    query = Reddit Search Query
    lmt = limit on number of posts
    lmt_comms = limit on posts' num of comments (if condition)
    
    Returns pandas dataframe with post's title, score, id, subreddit, url, number of comments, text body,
    and at which time i was created (to convert into datetime object use `datetime.utcfromtimestamp`)
    '''
    sub = reddit.subreddit(sub_name)
    api = PushshiftAPI(reddit_praw)
    posts = []
    for post in tqdm(api.search_submissions(subreddit = sub_name, after = afterdate, before = beforedate,
                                            q = query, mod_removed = False, user_removed = False, limit = lmt,
                                            filter = ["title", "score", "id", "subreddit", "num_comments", "body", "created"])):
        if post.selftext != '[removed]' and post.num_comments >= lmt_comms:
            posts.append([post.title,post.score, post.id, post.subreddit, post.num_comments, post.created])
    return(pd.DataFrame(posts, columns = ["title", "score", "id", "subreddit", "num_comments", "created"]))

def psaw_postcounter(reddit_praw, sub_name, query, afterdate, beforedate, lmt = 100, lmt_comms = 100):
    '''
    reddit_praw = reddit.Praw object (personalised)
    sub_name = Subreddit Name
    query = Reddit Search Query
    lmt = limit on number of posts
    lmt_comms = limit on posts' num of comments (if condition)
    '''
    sub = reddit.subreddit(sub_name)
    api = PushshiftAPI(reddit_praw)
    counter = 0
    limited_counter = 0
    for post in tqdm(api.search_submissions(subreddit = sub_name, after = afterdate, before = beforedate,
                                            q = query, mod_removed = False, user_removed = False, limit = lmt,
                                            filter = ["title", "id", "num_comments", "body", "created"])):
        counter += 1
        if post.selftext != '[removed]' and post.num_comments >= lmt_comms:
            limited_counter += 1
            
    if counter == lmt:
        print('Limit reached')
    return pd.DataFrame({'found_posts':counter, 'filtered_posts':limited_counter, 'pct_filtered':limited_counter/counter}, index = [1])

##psaw_postcounter returning dict instead and inputting api instead of reddit_praw model
def psaw_counter(psaw_api, sub_name, query, afterdate, beforedate, lmt = 100, lmt_comms = 100):
    '''
    reddit_praw = reddit.Praw object (personalised)
    sub_name = Subreddit Name
    query = Reddit Search Query
    lmt = limit on number of posts
    lmt_comms = limit on posts' num of comments (if condition)
    '''
    submissions = psaw_api.search_submissions(subreddit = sub_name, after = afterdate, before = beforedate, q = query, mod_removed = False,
                                              user_removed = False, limit = lmt, filter = ["title", "id", "num_comments", "body", "created"])
    limited_counter = 0
    counter = 0
    for post in submissions:
        counter += 1
        if post.selftext != '[removed]' and post.num_comments >= lmt_comms:
            limited_counter += 1
    if counter == lmt:
        print('Limit reached')
    return {'found_posts':counter, 'filtered_posts':limited_counter, 'pct_filtered':limited_counter/counter}


def order_gmeposts(df, aggs, sort):
    '''
    df = dataframe
    aggs = list of aggregation methods
    sort = tuple of multiindices
    '''
    df['date'] = [datetime.strftime(datetime.utcfromtimestamp(dt), '%Y-%m-%d') for dt in df['created']]
    return df.groupby('date').agg(aggs).sort_values(sort, ascending = False)

def getThreadsbyFlair(reddit_praw, sub_name, query, flair_text, afterdate, beforedate, lmt = 100):
    sub = reddit.subreddit(sub_name)
    api = PushshiftAPI(reddit_praw)
    posts = []
    for post in tqdm(api.search_submissions(subreddit = sub_name, after = afterdate, before = beforedate,
                                            q = query, mod_removed = False, user_removed = False, limit = lmt,
                                            filter = ["title", "id", "score", "num_comments", "link_flair_text", "created"])):
        if post.link_flair_text == flair_text:
            posts.append([post.title,post.score, post.id, post.subreddit, post.num_comments, post.link_flair_text, post.created])
    return pd.DataFrame(posts, columns = ["title", "score", "id", "subreddit", "num_comments", "link_flair_text", "created"])

def gme_savetocsv(df, sort, csvname, sep):
    df.sort_values(sort).to_csv(csvname, sep = sep)
    print(f"{csvname} was saved")
    
def eomday(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

#Function getting posts from a subreddit via a query
def getPosts(sub_name, query, lmt = 100):
    '''
    sub_name = Subreddit Name
    query = Reddit Search Query
    
    Returns pandas dataframe with post's title, score, id, subreddit, url, number of comments, text body,
    and at which time i was created (to convert into datetime object use `datetime.utcfromtimestamp`)
    '''
    sub = reddit.subreddit(sub_name)
    posts = []
    for post in tqdm(sub.search(query, limit = lmt)):
        posts.append([post.title,post.score, post.id, post.subreddit, post.url, post.num_comments,post.selftext, post.created])
    return(pd.DataFrame(posts, columns = ["title", "score", "id", "subreddit", "url", "num_comments", "body", "created"]).set_index("id"))

#function getting keycomments from a certain submisison using submission id
def getKeyComments(submission_id, keywords, lmt = 100, depth = 10):
    submission = reddit.submission(id = submission_id)
    keycomms = []
    submission.comments.replace_more(limit = depth)
    for comms in submission.comments[:lmt]:
        if any(keys in comms.body for keys in keywords):
            keycomms.append([comms.body, comms.id, comms.score])
    return(pd.DataFrame(keycomms, columns = ["body", "id", "score"]).set_index("id"))

def getComments(submission):
    submissions = [reddit.submission(id = thread) for thread in submission.id]
    comms_retrieved = []
    for thread in tqdm(submissions):
        comms_retrieved.append(len(thread.comments))
    return(pd.DataFrame(comms_retrieved))