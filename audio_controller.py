import threading
import uuid
import gtts
from playsound import playsound
import os

class AudioController:
    def __init__(self):
        self.audio_lock = threading.Lock()
        
    # takes in a string and plays it, removing the generated .wav file after playing
    def play_audio(self, voiceline):
      
        audio_blob = gtts.gTTS(text=voiceline, lang='en')
        file_name = str(uuid.uuid4()) + ".wav"
        audio_blob.save(file_name)
          
        # try playing the file & remove it after playing
        # playsound is blocking
        try:
          self.audio_lock.acquire()
          playsound(file_name)
          self.audio_lock.release()
          os.remove(file_name)
        except Exception as e:
          print(f"Could not play file: {e}")
      
    # given a file name, attempts to play it. If file DNE or is corrupted, throws an error
    def play_from_file(self, file_name):
        try:
            self.audio_lock.acquire()
            playsound(file_name)
            self.audio_lock.release()
        except Exception as e:
            raise Exception("Could not play audio file")
        
        
    def create_audio_file(self, voiceline, file_name):
        audio_blob = gtts.gTTS(text=voiceline, lang='en')
        fn = file_name + ".wav"
        audio_blob.save(fn)