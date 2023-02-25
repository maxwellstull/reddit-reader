import praw
import pandas as pd
import math
from praw.models import MoreComments
import gtts
import random
from playsound import playsound
import os
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from html2image import Html2Image
import csv
import pyttsx3 
import json
import shutil
import string
from Utility import ttsReq
from Utility import Objects

###Config 
# Top N comments to pull
COMMENTS = 10
# Clip duration
DURATION = 60
# Amount of submissions to pull per subreddit
LIMIT = 10
# End resolution, 720x1280 for TT and YTShorts
END_SIZE = (720,1280)
# mode for getting posts
MODE = 'csv' # 'csv', 'search', 'topday', 'topweek'
# DO NOT CHANGE PLEASE, its for how wide the generated html should be
shorts_width = int(END_SIZE[0] / 2)
# Experimental/in development setting for generated html
row_char_width=60
# Allegedly makes rendering faster the higher you put this number, so long as you have that many threads on your cpu
MULTITHREADING = 6
# Scale to upsize the comments
SCALE = 2




def main():
    print("uhh, hi")
    #### Initialize
    # tts requester
    requester = ttsReq.Requester()
    # reddit scraper
    reddit = praw.Reddit(client_id="wbOHDFUEwMZstfLaG0n08g",#my client id
                         client_secret="3IzxmpIJJpC80D4txcCAKHqXJDbV3A",  #your client secret
                         user_agent="my user agent", #user agent name
                         username = "",
                         password = "",
                         check_for_async=False) 
    # youtube shorts white background
    YTSB = Image.new('RGB',(END_SIZE[0],END_SIZE[1]),color='white')
    imgDraw = ImageDraw.Draw(YTSB)
    YTSB.save(os.getcwd() +'/YTSB.png')
    YTSBack = ImageClip(os.getcwd() + '/YTSB.png').set_duration(DURATION).set_start(0)
    
    engine = pyttsx3.init()
    engine.setProperty('rate',175)
    engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")
    
    with open('Utility/visitedposts.json','r') as fp:
        jason = json.load(fp)
    
    with open('Utility/bannedwords.txt','r') as fp:
        bad_words = {line.strip():None for line in fp.readlines()}
    
    def checkSubmission(submission):
        #if submission.id in jason:
        #    print("Skipping:\n ",submission.title,"\nBecause it has already been visited. (Post ID: ",submission.id,")")
        #    return False
        # Check if the text is too long
        if len(submission.selftext) > 200:
            print("Skipping:\n ",submission.title,"\nBecause there is too much text in the description. (Length: ",len(submission.selftext),")")
            return False
        # Check if there's banned words in the title or text
        dirty_mouth = False
        for word in submission.title.translate(submission.title.maketrans('','',string.punctuation)).split():
            if word in bad_words:
                dirty_mouth = True
        for word in submission.selftext.translate(submission.selftext.maketrans('','',string.punctuation)).split():
            if word in bad_words:
                dirty_mouth = True
        if dirty_mouth == True:
            return False
        return True
    
    #### Accumulate posts
    print("Beginning submission accumulation")
    submissions = []
    # Subreddits to search in if not using csv mode
    subs = ['AskReddit','ShowerThoughts', 'DoesAnybodyElse','todayilearned']
    if MODE == 'csv':
        with open('Utility/urls.csv','r') as fp:
            reader = csv.reader(fp)
            for i in reader:
                if checkSubmission(reddit.submission(url=str(i[0]))):
                    submissions.append(reddit.submission(url=str(i[0])))
    elif MODE == 'search':
        query = "fake"  ## Change this to get specific topics (like gaming or racing, etc)
        for sub in subs:
            for submission in reddit.subreddit(sub).search(query, time_filter='week',sort='top',limit=LIMIT):
                if checkSubmission(submission):
                    print(submission.title)
                    submissions.append(submission)
    elif MODE == 'topday':
        for sub in subs:
            for submission in reddit.subreddit(sub).top(time_filter='day',limit=LIMIT):
                if checkSubmission(submission):
                    submissions.append(submission)
    elif MODE == 'topweek':
        for sub in subs:
            for submission in reddit.subreddit(sub).top(time_filter='week',limit=LIMIT):
                if checkSubmission(submission):
                    submissions.append(submission)
    
    
    for submission in submissions:
        
        subreddit = submission.subreddit
        # Try to make a folder in the cwd of the subreddit name, for all posts from that subreddit to have relevant files in
        if not os.path.exists(os.getcwd() + "/" + str(subreddit.display_name)):
            os.mkdir(os.getcwd() + "/" + str(subreddit.display_name))
        print("Post:",submission.title)
    
        title_o = Objects.Title(submission.id, submission.score, submission.selftext,submission.subreddit,submission.title)
        title_o.process()
    
        comments = []
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue
            if comment.link_id != comment.parent_id:
                print("no", comment.link_id, comment.parent_id)
                continue
            
            # Check if comment is bad
            dirty_mouth = False
            for word in comment.body.translate(comment.body.maketrans('','',string.punctuation)).split():
                if word in bad_words:
                    dirty_mouth = True
            if dirty_mouth == False and len(comment.body) < 300:
                comment_obj = Objects.Comment(submission.id,comment.score,comment.body,submission.subreddit,comment.id)
                comment_obj.process()
                comments.append(comment_obj)
        comment_list = sorted(comments,reverse=True)[:COMMENTS]
        random.shuffle(comment_list)        
        
        pref = 1
        
        if pref == 0:
            engine.save_to_file(title_o.title,title_o.audio_file_path)
            engine.runAndWait()
        elif pref == 1:
            requester.make_job('WalterWhite',title_o.title)
            requester.poll_job_progress()
            requester.save_file(title_o.audio_file)
        for comment in comment_list:
            if pref == 0: #local engine
                engine.save_to_file(comment.text, comment.audio_file_path)
                engine.runAndWait()       
            elif pref == 1: #SLOW celebrity engine
                requester.make_job('WalterWhite',comment.text)
                requester.poll_job_progress()
                requester.save_file(comment.audio_file)
        
       
        mg = Objects.MediaGroups(title_o.getIC(),
                                 title_o.getAFC())
        mg.set_background_clip()
        mg.set_white_background(YTSBack)
        for comment in comment_list:
            mg.add_av(comment)
    
        mg.render_all(os.getcwd() + "/Videos/","YT"+str(submission.id)+".mp4")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()
    
    