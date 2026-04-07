import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate",175)
engine.setProperty("volume",1.0)

def speak(text):
    """Jarvis speaks a message out loud"""
    engine.say(text)
    engine.runAndWait()
    
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)

        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    except sr.WaitTimeoutError:
        return ""