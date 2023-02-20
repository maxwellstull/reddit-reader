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
from uploader import uploadVideo

#engine = pyttsx3.init()
#engine.setProperty('rate',150)
#engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")

# Top N comments to pull
COMMENTS = 20
# Clip duration
DURATION = 60
# Amount of submissions to pull per subreddit
LIMIT = 10
# End resolution, 720x1280 for TT and YTShorts
END_SIZE = (720,1280)
# mode for getting posts
MODE = 'topday' # 'csv', 'search', 'topday', 'topweek'
# DO NOT CHANGE PLEASE, its for how wide the generated html should be
shorts_width = int(END_SIZE[0] / 2)
# Experimental/in development setting for generated html
row_char_width=60
# Allegedly makes rendering faster the higher you put this number, so long as you have that many threads on your cpu
MULTITHREADING = 6
# Scale to upsize the comments
SCALE = 2

"""
Deals with title & description of a post
"""
class Title():
    # Initializer
    def __init__(self, submission_id,score,title,sub,engine,text=""):
        # Unique ID, alphanumeric
        self.id = submission_id
        # Amount of updoots
        self.score = score
        # Actual title text
        self.title = title
        # Post description
        self.text = text
        # Subreddit post is in
        self.subreddit = sub
        # TTS engine (potentially no longer needed here)
        self.engine = engine
        # Generates the path to the file that will hold the mp3 TTS once generated
        self.audio_file = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.id)+"/title.mp3"
        # Generates the path to the FOLDER that will hold the title screenshot
        self.image_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.id)+"/"
        
        # Generates height (in pixels) of the title screenshot. Still a WIP
        newlines=self.title.count("\n")
        strlen=len(self.title)
        rows = math.ceil(strlen/row_char_width)
        if self.text == "":
            self.image_height = 110+(rows*22)+(newlines*5)
        else:
            textrows = math.ceil(len(self.text) / 50)
            text_newlines = self.text.count("\n")
            self.image_height = 110+(rows*22)+(newlines*5)+(textrows*17)+(text_newlines*4)
    # Run TTS and SS
    def process(self):
        self.TTS()
        self.SS()
    # Text-to-speech generate and save. Currently having issue so the functionality
    #  has been brought out to the main function until I figure out why its doing it
    def TTS(self):
        #self.engine.save_to_file(self.title,self.audio_file)
        #self.engine.runAndWait()
        pass
    # Screenshot generate and save. 
    def SS(self):
        res = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=self.subreddit,postid=self.id,h=self.image_height)
        hti = Html2Image(output_path=self.image_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as='title.png')
    # Gets Audio File Clip
    def getAFC(self):
        self.af = AudioFileClip(self.audio_file)
        return self.af
    # Gets ImageClip, with the clip starting at the given start time
    #  Duration is entire time since we always have it up on the screen
    def getIC(self, start_time=0):
        bi = ImageClip(self.image_file_path + '/title.png')
        bi = bi.set_duration(DURATION)
        bi = bi.set_start(start_time)
        self.bi = bi.resize(SCALE)
        return self.bi
    # Currently not in use. Need to re-integrate it.
    def generateHTML(self,sub="",pid="",cid="",h=1):
        return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)
    # Functions for sort algorithm uses
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

"""
Class for comments and what they do
"""
class Comment():
    def __init__(self, cid,score,body,body_html,sub,submission_id,engine):
        # Comment ID, alphanumeric string
        self.id = cid
        # Comment updoots
        self.score = score
        # Comment text
        self.text = body
        # Comment text as html (no longer in use)
        self.html = body_html
        # Subreddit comment is in
        self.subreddit = sub
        # Post ID that comment is in
        self.sid = submission_id
        # TTS engine (depreciated)
        self.engine = engine
        # Generates the path to the file that will hold the mp3 TTS once generated
        self.audio_file = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.sid)+"/"+ str(self.id)+".mp3"
        # Generates the path to the FOLDER that will hold the title screenshot
        self.image_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.sid)
        # Generate screenshot image height. Still a WIP
        newlines=self.text.count("\n")
        strlen=len(self.text)
        rows = math.ceil(strlen/row_char_width)
        self.image_height = 110+(rows*20)+(newlines*5)
    # Run TTS and SS
    def process(self):
        self.TTS()
        self.SS()
    # Text-to-speech generate and save. Currently having issue so the functionality
    #  has been brought out to the main function until I figure out why its doing it
    def TTS(self):
        # self.engine.save_to_file(self.text,self.audio_file)
        # self.engine.runAndWait()
        pass     
    # Screenshot generate and save
    def SS(self):
        res=self.generateHTML(self.subreddit,self.sid,self.id,self.image_height)
        hti = Html2Image(output_path=self.image_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as=str(self.id)+'.png')
    # Get audio file clip
    def getAFC(self):
        self.af = AudioFileClip(self.audio_file)
        return self.af
    # Get image clip, with the start time as given and the duration being the total length of the audio clip
    def getIC(self, start_time=0):
        bi = ImageClip(self.image_file_path + '/' + str(self.id)+'.png')
        bi = bi.set_duration(self.af.duration)
        bi = bi.set_start(start_time)        
        self.bi = bi.resize(SCALE)
        return self.bi
    # Uses reddit embed html to generate pretty screenshot
    def generateHTML(self,sub="",pid="",cid="",h=1):
        return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)
    # Functions for sort algorithm uses
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


def get_tags(filename):
    if "minecraft" in filename:
        return ['minecraft','gaming','parkour']
    elif 'satisfying' in filename:
        return ['satisfying','sosatisfying','mmm','relaxing']
    elif 'trackmania' in filename:
        return ['gaming','racing','trackmania','speedrun']

       
def main():
    ##########
    # Initialize utilities
    ##########
    # Reddit scraper
    reddit = praw.Reddit(client_id="wbOHDFUEwMZstfLaG0n08g",#my client id
                         client_secret="3IzxmpIJJpC80D4txcCAKHqXJDbV3A",  #your client secret
                         user_agent="my user agent", #user agent name
                         username = "",
                         password = "",
                         check_for_async=False) 
    # Youtube Shorts background, a white background for verticle videos
    #  so that there isnt deadspace. This is the bottom layer of the composite video
    YTSB = Image.new('RGB',(END_SIZE[0],END_SIZE[1]),color='white')
    imgDraw = ImageDraw.Draw(YTSB)
    YTSB.save(os.getcwd() +'/YTSB.png')
    YTSBack = ImageClip(os.getcwd() + '/YTSB.png').set_duration(DURATION).set_start(0)
    # TTS engine
    engine = pyttsx3.init()
    engine.setProperty('rate',175)
    engine.setProperty('voice',"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0")
    # json file of posts that have already had videos made of them
    with open('visitedposts.json','r') as fp:
        jason = json.load(fp)
    # txt file of banned words. Inserted into dictionary for 
    #  quicker search times
    with open('bannedwords.txt','r') as fp:
        bad_words = {line.strip():None for line in fp.readlines()}
    
    # Function to check if we need to skip a post
    def checkSubmission(submission):
        if submission.id in jason:
            print("Skipping:\n ",submission.title,"\nBecause it has already been visited. (Post ID: ",submission.id,")")
            return False
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
    
    
    ##########
    # Accumulate the posts
    ##########
    print("Beginning submission accumulation")
    submissions = []
    # Subreddits to search in if not using csv mode
    subs = ['AskReddit','ShowerThoughts', 'DoesAnybodyElse','todayilearned']
    if MODE == 'csv':
        with open('urls.csv','r') as fp:
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
    upload_dump = []
    ##########
    # Do the stuff
    ##########
    print("Beginning submission processing")
    for submission in submissions:
        # Get subreddit object
        subreddit = submission.subreddit
        # Try to make a folder in the cwd of the subreddit name, for all posts from that subreddit to have relevant files in
        if not os.path.exists(os.getcwd() + "/" + str(subreddit.display_name)):
            os.mkdir(os.getcwd() + "/" + str(subreddit.display_name))
            
        ##########
        # Begin processing
        ##########
        print("Post:",submission.title)
        # Create title object & process
        title = Title(submission.id,submission.score,submission.title,submission.subreddit,engine,submission.selftext)
        title.process()
        # Create comment objects - for now every source comment (no replies) becomes an object.
        #  Inefficient but really fast compared to the time it takes to render the videos
        print("Creating comment objects")
        comments = []
        for comment in submission.comments:#.list():
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
                comment_obj = Comment(comment.id,comment.score,comment.body,comment.body_html,submission.subreddit,submission.id,engine)
                comments.append(comment_obj)
                
        ##########
        # Randomly select background video from content folder
        ##########
        print("Selecting background video")
        os.chdir("Content")
        file = random.choice(os.listdir())
        os.chdir("../")
        background_clip = VideoFileClip("Content/"+file)
        clip_start = random.randint(0,int(background_clip.duration-(DURATION+1)))
        background_clip = background_clip.subclip(clip_start,clip_start+DURATION)
        background_clip = background_clip.resize(width=END_SIZE[0])
        background_clip = background_clip.set_position((0, (END_SIZE[1]-background_clip.h)))

        ##########
        # Generate lists of clips
        ##########        
        # Video Clip list
        vcl = [YTSBack]
        # Audio Clip list
        acl = []
        # Generate title sound file
        engine.save_to_file(title.title,title.audio_file)
        engine.runAndWait()
        vcl.append(title.getIC())
        acl.append(title.getAFC())
        
        # This variable is used to determine the start time of the comment images. 
        #  Audio files are concatenated and dont need this, but the image files
        #  are composited (meaning they go on top of eachother) so in order
        #  to prevent them all from being displayed at once this is tracked
        next_start_ptr = title.getAFC().duration
        # Get top COMMENT comments and shuffle them so its not just descending
        comment_list = sorted(comments,reverse=True)[:COMMENTS]
        random.shuffle(comment_list)
        # This is where it becomes confusing, so try to keep up. Essentially, if we
        #  select the 10 top comments, and each comment takes 10 seconds to read,
        #  then we cant fit all the comments into 1 60-second video. So what this next
        #  section does is make numerous groups of clips and audios that will be
        #  rendered in different videos. So each video will have the same title image,
        #  title mp3, and white background, but the filler clip and the comments will 
        #  be different.
        vid_groups = []
        aud_groups = []
        tag_groups = [get_tags(file)]
        # Duplicate the common things and store them
        vid_group = vcl.copy()
        vid_group.append(background_clip)
        aud_group = acl.copy()
        # Iterate over comments
        print("Beginning clip sorting")
        for comment in comment_list:
            # Make comment mp3 file
            comment.process()
            engine.save_to_file(comment.text, comment.audio_file)
            engine.runAndWait()            
            # Get comment audio & image files
            af = comment.getAFC()
            vf = comment.getIC(next_start_ptr)
            # Calculate where to position the clip so its centered between title block and filler block
            title_offset = ((((END_SIZE[1] - background_clip.h)-(title.image_height*SCALE)) - vf.h)/2)+(title.image_height*SCALE)
            vf = vf.set_position((0, title_offset))
            # If this clip CANNOT fit in this video without it going over time limit            
            if next_start_ptr + af.duration > DURATION:
                # Add existing groups to list of lists, then reset them to title & background
                vid_groups.append(vid_group)
                aud_groups.append(aud_group)
                vid_group = vcl.copy()
                aud_group = acl.copy()
                # Repeat the process for getting the filler video
                os.chdir("Content")
                file = random.choice(os.listdir())
                os.chdir("../")
                tag_groups.append(get_tags(file))
                background_clip = VideoFileClip("Content/"+file)
                clip_start = random.randint(0,int(background_clip.duration-(DURATION+1)))
                background_clip = background_clip.subclip(clip_start,clip_start+DURATION)
                background_clip = background_clip.resize(width=END_SIZE[0])
                background_clip = background_clip.set_position((0, (END_SIZE[1]-background_clip.h)))
                vid_group.append(background_clip)
                # Calculate title offset again (in case filler height changed)
                title_offset = ((((END_SIZE[1] - background_clip.h)-(title.image_height*2)) - vf.h)/2)+(title.image_height*2)
                vf = vf.set_position((0, title_offset))
                # Find when this comment clip needs to start in the new video (right after title mp3 ends)
                next_start_ptr = title.getAFC().duration
                # Add THIS comment to the new groups
                vid_group.append(vf.set_start(next_start_ptr))
                aud_group.append(af)
                next_start_ptr = next_start_ptr + af.duration
            # If this comment CAN fit in this clip
            else:
                vid_group.append(vf)
                aud_group.append(af)
                next_start_ptr = next_start_ptr + af.duration
        # This condition catches that the final video to be assembled wont have the 
        #  'full' condition that results in it getting saved.
        if vid_group not in vid_groups:
            vid_groups.append(vid_group)
            aud_groups.append(aud_group)
            tag_groups.append(get_tags(file))
        # Iterate over the groupings of video and audio we made
        print((tag_groups))
        print(len(vid_groups))
        for i in range(0, len(vid_groups)):
            # Do some work
            videoclips = CompositeVideoClip(vid_groups[i])
            audioclips = concatenate_audioclips(aud_groups[i])
            videoclips = videoclips.set_audio(audioclips)
            # Trim clip in case audio doesnt go the full 60 seconds
            if audioclips.duration < DURATION:
                videoclips = videoclips.subclip(0, audioclips.duration)
            # If it is EXACTLY 60 seconds, make it 59.9 since youtube doesnt let 60 second vids into shorts (it thinks theyre longer i guess)
            else:
                videoclips = videoclips.subclip(0, DURATION-0.1)
            # Set fps to 30, you can have it at 60 if you want but itll double your render time
            videoclips = videoclips.set_fps(30)
            # Render
            videoclips.write_videofile(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/YT"+str(i)+"Short"+ str(submission.id)+".mp4", threads=MULTITHREADING)
            # Copy the video we just rendered into the Videos/ folder
            shutil.copyfile(os.getcwd() + "/" + str(subreddit.display_name)+ "/" + str(submission.id)+"/YT"+str(i)+"Short"+ str(submission.id)+".mp4", os.getcwd() + "/Videos" + "/YT"+str(i)+"Short"+ str(submission.id)+".mp4")
           
            # make title
            nouns = ['my uncle','my aunt','my dad','my dog','you','my mom','lebrons legacy','my mailman','my wrestling coach']
        
            adjectives = ['does','does not','cant','wont','will','shall']
            
            other_thing = ['understand','hate','get rich','like','respect','savor','appreciate']
            punctuation = ['???','!','!?','??!',"."]
            
            title = random.choice(nouns) + ' ' + random.choice(adjectives) + ' ' + random.choice(other_thing) + " this" + random.choice(punctuation)
            
            words = title.split(" ")
            choices = random.choices([j for j in range(len(words))],k=random.randint(1,3))
            for j in choices:
                words[j] = words[j].upper()
            title = " ".join(words)
            
            
            
            
            print("tag group: ", i)
            tags = tag_groups[i] + ['reddit','shorts','fyp','foryou']
            print("TITLE:",title)
            print("TAGS:",tags)
            
            
            
            
            upload_dump.append((title, tags, os.getcwd() + "/Videos" + "/YT"+str(i)+"Short"+ str(submission.id)+".mp4"))
            # Upload stuff
            #uploadVideo("da87f8fe38d2aa0b879212765977a961",os.getcwd() + "/Videos" + "/YT"+str(i)+"Short"+ str(submission.id)+".mp4", title, tags) 
           
        # Dump that we visited this file
        jason[submission.id] = True
        with open('visitedposts.json','w') as fp:
            json.dump(jason, fp)
    random.shuffle(upload_dump)
    for i in upload_dump:
        print("Uploading:", title, tags)
        #uploadVideo("da87f8fe38d2aa0b879212765977a961",i[2],i[0],i[1]) 
        
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    