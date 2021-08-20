###LIBRARY IMPORT
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk import pos_tag, ne_chunk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.probability import FreqDist
import contractions
import re
import string
import time
from emoji import UNICODE_EMOJI
from wordcloud import WordCloud
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
ps = PorterStemmer()
lem = WordNetLemmatizer()

###StopWords set
stopgme = stopwords.words('english') #extending stopwords for 'gme'
stopgme.extend(['gme'])

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

def cleantext(text):
    ###Remove reddit formatting and html links if present
    text = re.sub('\n','',re.sub(r'&#\S+',' ',re.sub(r'http\S+','', text)))
    ###Regular string cleaning
    ##Expand contractions, turn to lowercase, strip whitespace end and beginning
    text = contractions.fix(text).lower().strip()
    ##Remove punctuation using translate
    text = text.translate(str.maketrans('', '', string.punctuation))
    ##Remove digits
    text = re.sub("\d+","", text)
    return text
def translate_emoji(text):
    ###Hard loop thru all emojis replace with the corresponding translation
    for emoji in UNICODE_EMOJI['en'].keys():
        ###Adding extraspace at the end helps to seperate two emojis
        ##extra whitespaces are then stripped
        text = text.replace(emoji,"_".join(UNICODE_EMOJI['en'][emoji].replace(",","").replace(":","").split())+" ")
        text = text.strip()
    return text

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F" # emoticons
                           u"\U0001F300-\U0001F5FF" # symbols & pictographs
                           u"\U0001F680-\U0001F6FF" # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF" # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def processText(text, stopwords, emoji = False):
    ###Decide whether to translate or remove emojis by default removes emojis
    if emoji:
        cleaned = text.apply(lambda x: translate_emoji(cleantext(x)))
    else:
        cleaned = text.apply(lambda x: remove_emoji(cleantext(x)))
    ###Get tokens in pd.Series of list of tokens and as a string seperated by commas
    tokens = cleaned.apply(lambda x: [word for word in word_tokenize(x) if word not in stopwords])
    tokens_string = tokens.apply(lambda x: ",".join(x))
    ###Get Porter Stems
    stems = tokens.apply(lambda x: [ps.stem(word) for word in x])
    
    return pd.concat([cleaned, tokens_string, tokens, stems], axis = 1, keys = ['text_cleaned', 'tokens', 'tokens_list', 'porter_stems'])

def get_chunks(text, label):
    ''' 
    NE Type: Examples
    ORGANIZATION: Georgia-Pacific Corp., WHO
    PERSON: Eddy Bonte, President Obama
    LOCATION: Murray River, Mount Everest
    DATE: June, 2008-06-29
    TIME: two fifty a m, 1:30 p.m.
    MONEY: 175 million Canadian Dollars, GBP 10.40
    PERCENT: twenty pct, 18.75 %
    FACILITY: Washington Monument, Stonehenge
    GPE: South East Asia, Midlothian
    '''
    chunk = ne_chunk(pos_tag(word_tokenize(text)))
    chunklist = nltk.chunk.tree2conlltags(chunk)
    labelist = []
    for chunk in chunklist:
        if re.search(f'.-{label}', chunk[2]):
            labelist.append(chunk[0])
    return labelist

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------TEXT ANALYSIS CLASS---------------------------------------------------------

class TextAnalysis:
    def __init__(self, file):
        self.data = pd.read_csv(file, index_col = 0)
        self.processed_data = None
        self.word_freq = None
        
    ###Process Text using processData function
    def process_data(self, column, stopwords, emoji = False):

        if column == 'selftext':
            ###Condition of non removed/deleted/empty post content
            cond = (self.data[column].notna()) & (self.data[column] !='[removed]') & (self.data[column] !='[deleted]')
            ###Process text
            self.processed_data = processText(self.data.loc[cond, column], stopwords, emoji)
        elif column == 'title':
            self.processed_data = processText(self.data[column], stopwords, emoji)
    
    def getBigrams(self):
            
        self.bigrams = self.processed_data.tokens_list.apply(lambda x: [word for word in nltk.bigrams(x)])
        self.processed_data['bigrams_list'] = self.bigrams
        ###Flatten
        ##List of tuples --> FreqDist to get frequencies
        bigrams = [element for bigrams_list in self.bigrams for element in bigrams_list]
    
    def get_TickerMentions(self, plot = False, top = None, cmap = plt.rcParams['image.cmap']):
        '''
        Using both models of titles and posts' bodies searches for ticker mentions via simple regex string, where tickers
        are represented as up to 5 capital characters following '$'. Mainly picks up NYSE tickers.
        '''
        ###Filter posts' bodies for non-removed/deleted/empty posts
        cond = (self.data['selftext'].notna()) & (self.data['selftext'] !='[removed]') & (self.data['selftext'] !='[deleted]')
        body = self.data.loc[cond, 'selftext']
        ###Initialise dictionary to be written to
        ticker_mentions = {}

        ###Title loop
        for text in self.data.title:
            tickers = re.findall(r'\$\b[a-zA-Z]{1,5}\w\b', text)
            if tickers:
                for ticker in tickers:
                    if ticker in ticker_mentions.keys():
                        ticker_mentions[ticker] += 1
                    else:
                        ticker_mentions[ticker] = 1
        ###Body loop
        for text in body:
            tickers = re.findall(r'\$\b[a-zA-Z]{1,5}\w\b', text)
            if tickers:
                for ticker in tickers:
                    if ticker in ticker_mentions.keys():
                        ticker_mentions[ticker] += 1
                    else:
                        ticker_mentions[ticker] = 1
        
        data = sorted(ticker_mentions.items(), key = lambda x: x[1], reverse = True)
        
        if plot:
            fig, ax = plt.subplots(figsize = (12,8))
            limit = 10 if top is None else top
            colors = [plt.get_cmap(cmap)(i) for i in np.linspace(1, 0, len(data[:limit]))]

            for item, col in zip(data[:limit][::-1], colors):
                word,count = item
                ax.barh(y = re.sub('\$','',word), width = count, height = .8, color = col)
            plt.show()
        else:
            return data
            
    ###Get Word Frequency for 
    ##1.TOKENS
    def get_WordFrequency(self):
        self.word_freq = FreqDist([element for tokenlist in self.processed_data.tokens_list for element in tokenlist])
    ###2.PORTERSTEMS
    def get_PorterFrequency(self):
        self.porter_freq = FreqDist([element for porterlist in self.processed_data.porter_stems for element in porterlist])
    ##3.LEMMAS
    def get_LemmaFrequency(self):
        lemmas = self.process_data.tokens_list.apply(lambda x: [lem.lemmatize(token, "v") for token in x])
        self.lemma_freq = FreqDist([element for tokenlist in lemmas for element in tokenlist])
    ###Return TOP RESULTS
    #....
    
    ###Named Entity Recognition
    def chunking_NER(self, column, ne_type):
        '''
        Named Entity Recognition chunking method. For each row returns list of specified named entities.
        >2min runtime for 42k long dataframe
        '''
        return sub_apr.data[column].apply(get_chunks, args = [ne_type])
    ###Make frequence plots bar charts and simple plots
    def freq_plot(self, top, color = 'orange', title = ''):
        fig, ax = plt.subplots(figsize = (10,6))
        data = self.word_freq.most_common(top)
        
        for word, count in data:
            ax.bar(x = word, height = count, width = .8, color = color)
        
        ax.set_xlabel('Word')
        ax.set_ylabel('Count')
        
        ax.set_title(title)
    ###WordCloud
    
    def wordcloud(self, stopwords, backdrop = 'white', cmap = 'viridis'):
        fig, ax = plt.subplots(figsize = (10,6))
        
        ax.axis('off')
        ax.imshow(WordCloud(background_color = backdrop,
                            stopwords = stopwords,
                            width = 720,
                            height = 480,
                            colormap = cmap).generate_from_frequencies(self.word_freq),
                  interpolation = 'bilinear')
        plt.show()