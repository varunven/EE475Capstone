import gtts
from playsound import playsound

test = gtts.gTTS(text="Ghaith Boksmati", lang='en')
test.save("hello.wav")
playsound("hello.wav")
