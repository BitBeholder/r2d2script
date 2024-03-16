import speech_recognition as sr
from openai import OpenAI
import pyttsx3
from key import OPENAI_API_KEY

def capture_audio():
    # Initialize the recognizer
    r = sr.Recognizer()
    r.pause_threshold = 1.0  # Adjust this value based on testing; it represents the minimum length of silence (in seconds) that will be considered as the end of a phrase.

    # Capture audio from the microphone
    with sr.Microphone() as source:
        print("Please say something:")
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=60)  # Adjust 'timeout' and 'phrase_time_limit' as needed.
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None
        
    # Use Google's speech recognition
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

    return text

def get_chatgpt_response(text):

    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI with a sense of humor, programmed to answer people with short and sarcastic answers."},
                {"role": "user", "content": text}
            ]
        )
        response_message = chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting response from ChatGPT: {e}")
        response_message = "Sorry, I'm having trouble understanding you right now."
    return response_message

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    while True:
        input_text = capture_audio()
        if input_text is not None:
            response_text = get_chatgpt_response(input_text)
            speak_text(response_text)
        else:
            speak_text("I didn't catch that, could you please repeat?")

if __name__ == "__main__":
    main()