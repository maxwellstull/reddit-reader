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
import csv
import pyttsx3 


# Acessing the reddit api
COMMENTS = 10
END_SIZE = (720,1280)
MULTITHREADING = 6
DURATION = 60


engine = pyttsx3.init()
engine.setProperty('rate',150)
engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")


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


YTSB = Image.new('RGB',(END_SIZE[0],END_SIZE[1]),color='white')
imgDraw = ImageDraw.Draw(YTSB)
YTSB.save(os.getcwd() +'/YTSB.png')
YTSBack = ImageClip(os.getcwd() + '/YTSB.png').set_duration(DURATION).set_start(0)



submissions = []
with open('urls.csv','r') as fp:
    reader = csv.reader(fp)
    for i in reader:
        submissions.append(reddit.submission(url=str(i[0])))

for submission in submissions:
    subreddit = submission.subreddit



    try:
        os.mkdir(os.getcwd() + "/" + str(subreddit.display_name))
    except:
        pass

    # Dictionary to hold attributes from posts that we need
    post_dict = {
        "title" : [],
        "score" : [],
        "id" : [],
        "body" : [],
        "subreddit":[]
    }
    # Dictionary to hold attributes from comments
    comments_dict = {
        "id":[],
        "body":[],
        "score":[],
        "html":[],
    }
    print("Submission:", submission.title)
    # Make a folder for all the data (audio, images) of this submission
    try:
        os.mkdir(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id))
    except:
        pass
    
    # Save the info about the post that we want
    post_dict["title"].append(submission.title)
    post_dict["score"].append(submission.score)
    post_dict["id"].append(submission.id)
    post_dict["body"].append(submission.selftext)
    post_dict["subreddit"].append(submission.subreddit)
    
    # Save all the comments
    for comment in submission.comments.list():
        # something something skip the weird thing
        if isinstance(comment, MoreComments):
            continue
        # Save all the comment info we need
        comments_dict["id"].append(comment.id)
        comments_dict["body"].append(comment.body)
        comments_dict["score"].append(comment.score)
        comments_dict["html"].append(comment.body_html)
    # Move all the stuff we just got into a dataframe
    pc = pd.DataFrame(comments_dict)
    pc = pc.sort_values(by=["score"], ascending=False)
    pdi = pd.DataFrame(post_dict)
    
    # Text-to-speech & save of submission title
    engine.save_to_file(submission.title,os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/"+ "title.mp3")
    engine.runAndWait()
    # If there's a description, TTS & save
    if submission.selftext:
        engine.save_to_file(submission.selftext, os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/"+ "body.mp3")
        engine.runAndWait()
    # TTS & save of the top however many comments
    for i, row in pc.iloc[:COMMENTS].iterrows():
        engine.save_to_file(row.body, os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/"+ str(row.id)+".mp3")
        engine.runAndWait()
    # Little cheese boy that chooses when the audio clips start
    next_start_ptr = 0

    # Randomly select background video from content folder
    os.chdir("Content")
    file = random.choice(os.listdir())
    os.chdir("../")
    clipy = VideoFileClip("Content/"+file)            
    clipstart = random.randint(0, int(clipy.duration-(DURATION+30)))
    clipy = VideoFileClip("Content/"+file).subclip(clipstart, clipstart+DURATION)
    # Resizing and positioning to be at bottom
    clipy = clipy.resize(width=END_SIZE[0])
    clipy = clipy.set_position((0,(END_SIZE[1]-clipy.h)))
    # YTSBack is just a white background the size of a youtube shorts video, so we dont have to worry about any sizing stuff
    clip = [YTSBack,clipy]
    
    # List of audioclips that we gonna collect
    audioclips = []
    # Obtain title TTS file
    titleTTS = AudioFileClip(os.getcwd()+ "/" + str(subreddit.display_name) + "/" + str(submission.id)+"/"+ "title.mp3")
    # Generate how long the title block should be
    text = submission.title
    newlines = text.count("\n")
    strlen = len(text)
    rows = math.ceil(strlen / 50)
    title_delta = 70+(rows*23)+(newlines*10)
    # Generate and take screenshot of title block
    hti = Html2Image(output_path=os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id),size=(360,title_delta))
    title_html = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=submission.subreddit,postid=submission.id,h=title_delta*2)
    hti.screenshot(html_str=title_html, save_as='title.png')
    # Put the image as a clip, double it and give it to the next person
    titleimage = ImageClip(os.getcwd()+ "/" + str(subreddit.display_name) + "/" + str(submission.id)+'/title.png').set_duration(DURATION).set_start(next_start_ptr)
    titleimage = titleimage.resize(2)
    next_start_ptr = next_start_ptr + titleTTS.duration
    # Add the title stuff to the collection of clips
    clip.append(titleimage)
    audioclips.append(titleTTS)
    clippies = clip
    # Go over all the comments and do what we did for the title
    for i, row in pc.iloc[:COMMENTS].iterrows():
        # Get audiofile
        af = AudioFileClip(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/"+ str(row.id)+".mp3")
        audioclips.append(af)
        # Figure out screenshot size
        text = row.body
        newlines = text.count("\n")
        strlen = len(text)
        rows = math.ceil(strlen / 60)
        height = 110+(rows*20)+(newlines*5)
        # Do it        
        res = generateHTML(submission.subreddit,submission.id,row.id,h=height)
        hti = Html2Image(output_path=os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id),size=(360,height))
        hti.screenshot(html_str=res, save_as=str(row.id)+'.png')
        # Clip thing
        bodyimage = ImageClip(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+'/' + str(row.id)+'.png').set_duration(af.duration).set_start(next_start_ptr)
        # Generate position
        x = 0
        y = title_delta + 200
                
        bodyimage = bodyimage.set_position((x,y))
        bodyimage = bodyimage.resize(2)
        next_start_ptr = next_start_ptr + af.duration
        clippies.append(bodyimage)
        
        
    clip = CompositeVideoClip(clippies)
    audioclipy = concatenate_audioclips(audioclips)
    clip = clip.set_audio(audioclipy)
    #final_clip = concatenate_videoclips([clip])
    if next_start_ptr < DURATION:
        clip = clip.subclip(0, next_start_ptr + 0.5)
    clip = clip.subclip(0, 59.5)
    clip = clip.set_fps(30)
    clip.write_videofile(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/YTShort"+ str(submission.id)+".mp4", threads=MULTITHREADING)







        
        