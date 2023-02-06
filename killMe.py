#######
# IMPORT PACKAGES
#######

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


# Acessing the reddit api
COMMENTS = 1
END_SIZE = (1280,720)
MULTITHREADING = 6

def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def generateHTML(sub="",pid="",cid="",h=300):
    return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="640" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)





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
        
        for submission in subreddit.search(query,limit = 1):
            post_dict = {
                "title" : [],
                "score" : [],
                "id" : [],
                "body" : [],
                "subreddit":[]
            }
            comments_dict = {
                "id":[],
                "body":[],
                "score":[],
                "html":[],
            }
            print("TITLE:", submission.title)
            try:
                os.mkdir(os.getcwd() + "/" + str(submission.id)+"/")
            except:
                pass
            print(submission.score)
            post_dict["title"].append(submission.title)
            post_dict["score"].append(submission.score)
            post_dict["id"].append(submission.id)
            #post_dict["url"].append(submission.url)
            #post_dict["comms_num"].append(submission.num_comments)
            #post_dict["created"].append(submission.created)
            post_dict["body"].append(submission.selftext)
            post_dict["subreddit"].append(submission.subreddit)
            
            ##### Acessing comments on the post
#            submission.comments.replace_more(limit = 1)
            
            for comment in submission.comments.list():
                if isinstance(comment, MoreComments):
                    continue
                comments_dict["id"].append(comment.id)
                comments_dict["body"].append(comment.body)
                comments_dict["score"].append(comment.score)
                comments_dict["html"].append(comment.body_html)
            pc = pd.DataFrame(comments_dict)
            pc = pc.sort_values(by=["score"], ascending=False)
            
            tts = gtts.gTTS(submission.title)
            tts.save(os.getcwd() + "/" + str(submission.id)+"/"+ "title.mp3")
            if submission.selftext:
                tts = gtts.gTTS(submission.selftext)
                tts.save(os.getcwd() + "/" + str(submission.id)+"/"+ "body.mp3")
            
            for i, row in pc.iloc[:COMMENTS].iterrows():
                tts = gtts.gTTS(row.body)
                tts.save(os.getcwd() + "/" + str(submission.id)+"/"+ str(row.id)+".mp3")
            pdi = pd.DataFrame(post_dict)
#            pc.to_csv(os.getcwd() + "/" + str(submission.id)+"/"+"comments.csv")
#            pdi.to_csv(os.getcwd() + "/" + str(submission.id)+"/"+"post.csv")

            next_start_ptr = 0

            clipstart = random.randint(0, 55)
            clip = VideoFileClip("filler.mp4").subclip(clipstart*60, (clipstart*60)+120)
            clip = clip.resize(END_SIZE)
            
            audioclips = []
            titleTTS = AudioFileClip(os.getcwd() + "/" + str(submission.id)+"/"+ "title.mp3")


            
            

            text = submission.selftext
            newlines = text.count("\n")
            strlen = len(text)
            rows = math.ceil(strlen / 105)
            title_delta = 130+(rows*14)+(newlines*10)
            
            
            hti = Html2Image(output_path=os.getcwd() + "/" + str(submission.id),size=(640,title_delta))
            title_html = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="640" height="{h}"></iframe>""".format(sub=submission.subreddit,postid=submission.id,h=title_delta)
            hti.screenshot(html_str=title_html, save_as='title.png')
            
            titleimage = ImageClip(os.getcwd() + "/" + str(submission.id)+'/title.png').set_duration(clip.duration).set_start(next_start_ptr)
            next_start_ptr = next_start_ptr + titleTTS.duration
            clip = CompositeVideoClip([clip, titleimage])

            audioclips.append(titleTTS)
                
                
                
            for i, row in pc.iloc[:COMMENTS].iterrows():
                af = AudioFileClip(os.getcwd() + "/" + str(submission.id)+"/"+ str(row.id)+".mp3")
                audioclips.append(af)
                text = row.body

                newlines = text.count("\n")
                strlen = len(text)
                rows = math.ceil(strlen / 105)
                
                res = generateHTML(submission.subreddit,submission.id,row.id,h=130+(rows*13)+(newlines*10))
                hti = Html2Image(output_path=os.getcwd() + "/" + str(submission.id),size=(640,130+(rows*13)+(newlines*10)))
                hti.screenshot(html_str=res, save_as=str(row.id)+'.png')
                
                                
                
                bodyimage = ImageClip(os.getcwd() + "/" + str(submission.id)+'/' + str(row.id)+'.png').set_duration(af.duration).set_start(next_start_ptr)
        
                x = (END_SIZE[0] - abs(bodyimage.w))/2
                y = (((END_SIZE[1] - title_delta) - abs(bodyimage.h)) / 2) + title_delta
                
                bodyimage = bodyimage.set_position((x,y))
                next_start_ptr = next_start_ptr + af.duration
                clip = CompositeVideoClip([clip, bodyimage])
                
                
                
            
            audioclipy = concatenate_audioclips(audioclips)
            clip = clip.set_audio(audioclipy)
            final_clip = concatenate_videoclips([clip])
            final_clip.write_videofile(os.getcwd() + "/" + str(submission.id)+"/"+ str(submission.id)+".mp4", threads=MULTITHREADING)






        
        
        