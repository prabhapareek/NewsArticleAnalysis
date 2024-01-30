import feedparser as fp
import json
import nltk
# import pandas as pd
# import numpy as np 

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
# nltk.download('stopwords')

# from nltk.corpus import stopwords
# stop_word = set(stopwords.words('english'))
# print(stop_words)


base = declarative_base()
class Article(base):
    __tablename__ = 'articles'
    
    id = Column('ID', Integer)
    title = Column('Title', String, primary_key = True)
    description = Column('Description',String )
    pubdate = Column('PublicationDate ', String)
    sourceURL = Column('SourceURL', String)
    sentiment = Column('Category', String)

    def __init__(self, id, title, description, pubdate, sourceURL, sentiment=""):
        self.id = id
        self.title = title
        self.description = description
        self.pubdate = pubdate
        self.sourceURL = sourceURL
        self.sentiment = sentiment
        

    def __repr__(self):
       return f'({self.title}, {self.description}, {self.pubdate}, {self.sourceURL}, {self.sentiment})'
    
engine = create_engine("sqlite:///mydb.db", echo=True, poolclass=NullPool)
base.metadata.create_all(bind=engine)

Session = sessionmaker(bind = engine)
session = Session()
BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
rss_url = ['http://rss.cnn.com/rss/cnn_topstories.rss',
           'http://qz.com/feed',
           'http://feeds.foxnews.com/foxnews/politics',
           'http://feeds.reuters.com/reuters/businessNews',
           'http://feeds.feedburner.com/NewshourWorld',
           'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
           ]
n = 1
for url in rss_url:
    #print(url)
    feed = fp.parse(url)
    #print(feed.keys())
    items = feed.entries
    
    try:
        with open(f'items{n}.json', 'w') as f:
            json.dump(items,fp = f, indent=4)
    except Exception as e:
        continue
    n += 1
    #titles = []
    #descriptions = []
    #pubdate = []
    #sourceURL = []
    for item in items:
        id = item.id

        
        # words_without_stopwords = []
        # for word in word_tokenize:
        #     if word in stop_word:
        #         words_without_stopwords.append(word)
        # print(set(tokenize_words)-set(words_without_stopwords))


        

        try:
            title = item.title
        except Exception as e:
            title = ""
        try:
            description = item.summary
            sia = SentimentIntensityAnalyzer()
            res = sia.polarity_scores(description)
            if res['pos'] > res['neg']:
                sentiment = 'positive'
            elif res['neg'] > res['pos']:
                sentiment = 'negetive'
            else:
                sentiment = 'neutral'
            
            tokenize_words = word_tokenize(description)
            print(tokenize_words)
        except Exception as e:
            description = ""
            sentiment = ""
        try:
            pubDate = item.published
            print(pubDate)
        except Exception as e:
            pubDate = ""
        try:
            link = item.link
        except Exception as e:
            link = ""
        
        article = Article(id, title, description, pubDate, link, sentiment)
        session.add(article)

    try:    
        session.commit()
    except Exception as e:
        continue

        #print(item)
        #titles.append(item.title)
        #descriptions.append(item.description)
        #pubdate.append(item.pubDate) 
        #sourceURL.append(item.link)
    #print(titles)
    #print(descriptions)
    #print(pubdate)
    #print(sourceURL)

    #break
    #print(feed.status)

#Parse each feed and extract relevant information from each news article,
#including title, content, publication date, and source URL.
    


    


