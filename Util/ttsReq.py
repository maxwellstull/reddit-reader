import requests
import json
import time
from uuid import uuid4



class Requester():
    def __init__(self):
        self.headers = {"accept":"application/json","content-Type": "application/json"}
        self.session = requests.Session()
        self.session.headers = self.headers
        
        self.voices = {
            'Obama':'TM:58vtv7x9f32c',
            'BenShapiro':'TM:nqwew67rzwz4',
            'Trump':'TM:pyzss4phqk6r',
            'Gottfried':'TM:d7anwftbpjqm',
            'WalterWhite':'TM:8afk285jc2gs'}
    def make_job(self, voice, text):
        if voice not in self.voices:
            return False
        
        payload = {"uuid_idempotency_token":str(uuid4()),"tts_model_token":self.voices[voice],"inference_text":text}
        result = self.session.post(url='https://api.fakeyou.com/tts/inference', data=json.dumps(payload))
        if result.status_code==200:
            self.job_token = result.json()["inference_job_token"]
            return True
        return False
    
    def poll_job_progress(self):
        result = self.session.get("https://api.fakeyou.com/tts/job/{tok}".format(tok=self.job_token))
        result_dict = json.loads(result.text)
        while result_dict['state']['status'] == 'pending' or result_dict['state']['status'] == 'started':
            time.sleep(5)
            result = self.session.get("https://api.fakeyou.com/tts/job/{tok}".format(tok=self.job_token))
            result_dict = json.loads(result.text)
            print(result_dict['state']['status'])
        if result_dict['state']['status'] == 'complete_success':
            self.path = 'https://storage.googleapis.com/vocodes-public' + result_dict['state']['maybe_public_bucket_wav_audio_path']
    def save_file(self,title):
        r = requests.get(self.path)
        open("{title}".format(title=title),'wb').write(r.content)