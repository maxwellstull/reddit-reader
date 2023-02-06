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
END_SIZE = (720,1280)
MULTITHREADING = 6
DURATION = 10

def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def generateHTML(sub="",pid="",cid="",h=300):
    return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=2*h)





reddit = praw.Reddit(client_id="wbOHDFUEwMZstfLaG0n08g",#my client id
                     client_secret="3IzxmpIJJpC80D4txcCAKHqXJDbV3A",  #your client secret
                     user_agent="my user agent", #user agent name
                     username = "",     # your reddit username
                     password = "",
                     check_for_async=False)     # your reddit password

sub = ['Askreddit']  # make a list of subreddits you want to scrape the data from



# if submission.selftext:
#     bodyTTS = AudioFileClip(os.getcwd() + "/" + str(submission.id)+"/"+ "body.mp3")
#     audioclips.append(bodyTTS)
    
#     message = submission.selftext
#     img = Image.new('RGB',(width,height),color='white')
#     imgDraw = ImageDraw.Draw(img)
#     imgDraw.text((0,0), message, fill=(0,0,0),font=ImageFont.truetype("arial.ttf",size=20))  #320 x 180
#     img.save(os.getcwd() + "/" + str(submission.id)+'/body.png')
    
#     bodyimage = ImageClip(os.getcwd() + "/" + str(submission.id)+'/body.png').set_duration(bodyTTS.duration).set_start(next_start_ptr)
#     next_start_ptr = next_start_ptr + bodyTTS.duration
#     clip = CompositeVideoClip([clip, bodyimage])


YTSB = Image.new('RGB',(END_SIZE[0],END_SIZE[1]),color='white')
imgDraw = ImageDraw.Draw(YTSB)
YTSB.save(os.getcwd() +'/YTSB.png')
    
YTSBack = ImageClip(os.getcwd() + '/YTSB.png').set_duration(DURATION).set_start(0)




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

            clipstart = random.randint(0, 10)
            clipy = VideoFileClip("filler.mp4").subclip(clipstart*60, (clipstart*60)+DURATION)
            clipy = clipy.resize(width=END_SIZE[0])
            clipy = clipy.set_position((0,(END_SIZE[1]-clipy.h)))
            
            clip = [YTSBack,clipy]
            
            audioclips = []
            titleTTS = AudioFileClip(os.getcwd() + "/" + str(submission.id)+"/"+ "title.mp3")

        
            
            

            text = submission.selftext
            newlines = text.count("\n")
            strlen = len(text)
            rows = math.ceil(strlen / 105)
            title_delta = 130+(rows*14)+(newlines*10)
            
            
            hti = Html2Image(output_path=os.getcwd() + "/" + str(submission.id),size=(360,title_delta))
            title_html = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=submission.subreddit,postid=submission.id,h=title_delta*2)
            hti.screenshot(html_str=title_html, save_as='title.png')
            
            titleimage = ImageClip(os.getcwd() + "/" + str(submission.id)+'/title.png').set_duration(DURATION).set_start(next_start_ptr)
            titleimage = titleimage.resize(2)
            next_start_ptr = next_start_ptr + titleTTS.duration
            
            
            
            
            
            
            clip.append(titleimage)

            audioclips.append(titleTTS)
                
                
            clippies = clip
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
                x=0
                y = title_delta + 200
                
                bodyimage = bodyimage.set_position((x,y))
                bodyimage = bodyimage.resize(2)
                next_start_ptr = next_start_ptr + af.duration
                clippies.append(bodyimage)
                
                
                
            clip = CompositeVideoClip(clippies)
            audioclipy = concatenate_audioclips(audioclips)
            clip = clip.set_audio(audioclipy)
            #final_clip = concatenate_videoclips([clip])
            clip.write_videofile(os.getcwd() + "/" + str(submission.id)+"/YTShort"+ str(submission.id)+".mp4", threads=MULTITHREADING)






        
        
        