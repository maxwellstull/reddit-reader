#######
# IMPORT PACKAGES
#######

import praw
import pandas as pd
from praw.models import MoreComments
import gtts
from playsound import playsound

# Acessing the reddit api


reddit = praw.Reddit(client_id="wbOHDFUEwMZstfLaG0n08g",#my client id
                     client_secret="3IzxmpIJJpC80D4txcCAKHqXJDbV3A",  #your client secret
                     user_agent="my user agent", #user agent name
                     username = "",     # your reddit username
                     password = "",
                     check_for_async=False)     # your reddit password

sub = ['Askreddit']  # make a list of subreddits you want to scrape the data from

for s in sub:
    subreddit = reddit.subreddit(s)   # Chosing the subreddit


########################################
#   CREATING DICTIONARY TO STORE THE DATA WHICH WILL BE CONVERTED TO A DATAFRAME
########################################

#   NOTE: ALL THE POST DATA AND COMMENT DATA WILL BE SAVED IN TWO DIFFERENT
#   DATASETS AND LATER CAN BE MAPPED USING IDS OF POSTS/COMMENTS AS WE WILL 
#   BE CAPTURING ALL IDS THAT COME IN OUR WAY

# SCRAPING CAN BE DONE VIA VARIOUS STRATEGIES {HOT,TOP,etc} we will go with keyword strategy i.e using search a keyword
    query = ['Gaming']

  #  result = subreddit.search(query, sort="top", limit=1)
  #  print(result)

        
    for item in query:
        post_dict = {
            "title" : [],
            "score" : [],
            "id" : [],
            "url" : [],
            "comms_num": [],
            "created" : [],
            "body" : []
        }
        comments_dict = {
            "id":[],
            "body":[],
            "score":[],
        }
        for submission in subreddit.search(query,limit = 1):
            print("TITLE:", submission.title)
            print(submission.score)
            # post_dict["title"].append(submission.title)
            # post_dict["score"].append(submission.score)
            # post_dict["id"].append(submission.id)
            # post_dict["url"].append(submission.url)
            # post_dict["comms_num"].append(submission.num_comments)
            # post_dict["created"].append(submission.created)
            # post_dict["body"].append(submission.selftext)
            
            ##### Acessing comments on the post
#            submission.comments.replace_more(limit = 1)
            
            for comment in submission.comments.list():
                if isinstance(comment, MoreComments):
                    continue
                comments_dict["id"].append(comment.id)
                comments_dict["body"].append(comment.body)
                comments_dict["score"].append(comment.score)
        
        pc = pd.DataFrame(comments_dict)
        pc = pc.sort_values(by=["score"], ascending=False)
        print(pc)
        
        tts = gtts.gTTS("hello, world")
        tts.save("hello.mp3")
        playsound("hello.mp3")
        
        