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


engine = pyttsx3.init()
engine.setProperty('rate',150)
engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")

COMMENTS = 10
DURATION = 60
END_SIZE = (720,1280)
row_char_width=60
shorts_width = int(END_SIZE[0] / 2)
MULTITHREADING = 6
MODE = 'csv' # 'csv', 'search', 'topday', 'topweek'

class Title():
    def __init__(self, submission_id,score,title,sub,engine,text=""):
        self.id = submission_id
        self.score = score
        self.title = title
        self.subreddit = sub
        self.engine = engine
        self.text = text
        
        self.audio_file = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.id)+"/title.mp3"
        self.image_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.id)+"/"
        newlines=self.title.count("\n")
        strlen=len(self.title)
        rows = math.ceil(strlen/row_char_width)
        if self.text == "":
            self.image_height = 110+(rows*22)+(newlines*5)
        else:
            textrows = math.ceil(len(self.text) / 50)
            text_newlines = self.text.count("\n")
            self.image_height = 110+(rows*22)+(newlines*5)+(textrows*17)+(text_newlines*4)
    def process(self):
        self.TTS()
        self.SS()
    def TTS(self):
        pass
        #self.engine.save_to_file(self.title,self.audio_file)
        #self.engine.runAndWait()
    def SS(self):
        res=title_html = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=self.subreddit,postid=self.id,h=self.image_height)
                        #    <iframe id="reddit-embed" src="https://www.redditmedia.com/r/AskMen/comments/10v90en/men_whats_your_opinionss_on_homie_hoppers/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="640" height="166"></iframe>
        hti = Html2Image(output_path=self.image_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as='title.png')
    def getAFC(self):
        self.af = AudioFileClip(self.audio_file)
        return self.af
    def getIC(self, start_time=0):
        bi = ImageClip(self.image_file_path + '/title.png')
        bi = bi.set_duration(DURATION)
        bi = bi.set_start(start_time)
        self.bi = bi.resize(2)
        return self.bi
 
    def generateHTML(self,sub="",pid="",cid="",h=1):
        return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)
    def __lt__(self, obj):
        return ((self.score) < (obj.score))  
    def __gt__(self, obj):
        return ((self.score) > (obj.score))
    def __le__(self, obj):
        return ((self.score) <= (obj.score))  
    def __ge__(self, obj):
        return ((self.score) >= (obj.score))  
    def __eq__(self, obj):
        return (self.score == obj.score)
    
class Comment():
    def __init__(self, cid,score,body,body_html,sub,submission_id,engine):
        self.id = cid
        self.score = score
        self.text = body
        self.html = body_html
        self.subreddit = sub
        self.sid = submission_id
        self.engine = engine
            
        self.audio_file = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.sid)+"/"+ str(self.id)+".mp3"
        self.image_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.sid)
        newlines=self.text.count("\n")
        strlen=len(self.text)
        rows = math.ceil(strlen/row_char_width)
        self.image_height = 110+(rows*20)+(newlines*5)
    def process(self):
        self.TTS()
        self.SS()
    def TTS(self):
        pass
        #self.engine.save_to_file(self.text,self.audio_file)
        # self.engine.runAndWait()
    def SS(self):
        res=self.generateHTML(self.subreddit,self.sid,self.id,self.image_height)
        hti = Html2Image(output_path=self.image_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as=str(self.id)+'.png')
    def getAFC(self):
        self.af = AudioFileClip(self.audio_file)
        return self.af
    def getIC(self, start_time=0):
        bi = ImageClip(self.image_file_path + '/' + str(self.id)+'.png')
        bi = bi.set_duration(self.af.duration)
        bi = bi.set_start(start_time)
        
        self.bi = bi.resize(2)
        return self.bi
    def generateHTML(self,sub="",pid="",cid="",h=1):
        return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)
    def __lt__(self, obj):
        return ((self.score) < (obj.score))  
    def __gt__(self, obj):
        return ((self.score) > (obj.score))  
    def __le__(self, obj):
        return ((self.score) <= (obj.score))  
    def __ge__(self, obj):
        return ((self.score) >= (obj.score))
    def __eq__(self, obj):
        return (self.score == obj.score)
    def __repr__(self):
        return str(self.score)
        
       
def main():
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
    
    engine = pyttsx3.init()
    engine.setProperty('rate',150)
    engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")
    
    with open('visitedposts.json','r') as fp:
        jason = json.load(fp)
    with open('bannedwords.txt','r') as fp:
        bad_words = {line.strip():None for line in fp.readlines()}
    print(bad_words)
    
    
    submissions = []
    subs = ['AskReddit','AmITheAsshole']
    if MODE == 'csv':
        with open('urls.csv','r') as fp:
            reader = csv.reader(fp)
            for i in reader:
                submissions.append(reddit.submission(url=str(i[0])))
    elif MODE == 'search':
        query = "?"
        for sub in subs:
            for submission in reddit.subreddit(sub).search(query, time_filter='week',sort='top',limit=10):
                submissions.append(submission)
    elif MODE == 'topday':
        for sub in subs:
            for submission in reddit.subreddit(sub).top(time_filter='day'):
                submissions.append(submission)
    elif MODE == 'topweek':
        for sub in subs:
            for submission in reddit.subreddit(sub).top(time_filter='week'):
                submissions.append(submission)

    for submission in submissions:
        subreddit = submission.subreddit
        
        if not os.path.exists(os.getcwd() + "/" + str(subreddit.display_name)):
            os.mkdir(os.getcwd() + "/" + str(subreddit.display_name))

        if submission.id in jason:
            print("Skipping because we already rendered for this")
            continue
        
        print("Post:",submission.title)
        title = Title(submission.id,submission.score,submission.title,submission.subreddit,engine,submission.selftext)
        title.process()
        comments = []
        print("Comments:",len(submission.comments.list()))
        for comment in submission.comments.list():
            if isinstance(comment, MoreComments):
                continue
            dirty_mouth = False
            for word in comment.body.split():
                if word in bad_words:
                    dirty_mouth = True
            
            if dirty_mouth == False:
                comment = Comment(comment.id,comment.score,comment.body,comment.body_html,submission.subreddit,submission.id,engine)
                comments.append(comment)
        print("Done with comments")
        ##########
        # Randomly select background video from content folder
        os.chdir("Content")
        file = random.choice(os.listdir())
        os.chdir("../")
        background_clip = VideoFileClip("Content/"+file)
        clip_start = random.randint(0,int(background_clip.duration-(DURATION+1)))
        background_clip = background_clip.subclip(clip_start,clip_start+DURATION)
        background_clip = background_clip.resize(width=END_SIZE[0])
        background_clip = background_clip.set_position((0, (END_SIZE[1]-background_clip.h)))
        
        vcl = [YTSBack, background_clip] # video clip list
        acl = []    # audio clip list
        
        engine.save_to_file(title.title,title.audio_file)
        engine.runAndWait()
        vcl.append(title.getIC())
        acl.append(title.getAFC())
        
        
        next_start_ptr = title.getAFC().duration
        
        comment_list = sorted(comments,reverse=True)[:COMMENTS]
        random.shuffle(comment_list)
        print(comment_list)
        for comment in comment_list:
            comment.process()
            engine.save_to_file(comment.text, comment.audio_file)
            engine.runAndWait()            
            
            
            
            af = comment.getAFC()
            vf = comment.getIC(next_start_ptr)
            title_offset = ((((END_SIZE[1] - background_clip.h)-(title.image_height*2)) - vf.h)/2)+(title.image_height*2)
            vf = vf.set_position((0, title_offset))
            
            next_start_ptr = next_start_ptr + af.duration
            
            vcl.append(vf)
            acl.append(af)
            
        videoclips = CompositeVideoClip(vcl)
        audioclips = concatenate_audioclips(acl)
        videoclips = videoclips.set_audio(audioclips)
        if next_start_ptr < DURATION:
            videoclips = videoclips.subclip(0, next_start_ptr + 0.5)
        else:
            videoclips = videoclips.subclip(0, DURATION-0.1)
        videoclips = videoclips.set_fps(30)
        videoclips.write_videofile(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/YTShort"+ str(submission.id)+".mp4", threads=MULTITHREADING)
       
        shutil.copyfile(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/YTShort"+ str(submission.id)+".mp4", os.getcwd() + "/Videos" + "/YTShort"+ str(submission.id)+".mp4")
       
        # this is temporary for development. once dev is done, json will load and dump only ONCE
        # but because i stop the script so often its gonna do it every time
        
        jason[submission.id] = True
        with open('visitedposts.json','w') as fp:
            json.dump(jason, fp)
        
        
if __name__ == "__main__":
    main()
    