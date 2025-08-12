import os
import time
import speech_recognition as sr
from gtts import gTTS
import playsound
import google.generativeai as genai
import tempfile
import requests

# ---------------------------
# 1. Gemini API Setup (Hardcoded key)
# ---------------------------
API_KEY = "AIzaSyAMvbkoDRbI1k6zk0qJ9DRBkhQvO39NnSA"  # Replace with your Gemini API key
if not API_KEY.strip():
    raise ValueError("❌ No Gemini API key provided in the script.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------
# 2. Weather API Setup
# ---------------------------
WEATHER_API_KEY = "29fbc9e71e852924b8b82bc174743196"  # Replace with your OpenWeatherMap API key

def get_weather(city):
    """Fetch real-time weather for a given city."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return f"Sorry, I couldn't find weather data for {city}."

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Okay, in {city} it is {temp}°C with {desc}."
    except Exception as e:
        return "Sorry, I couldn't fetch the weather right now."

# ---------------------------
# Optional wake word
# ---------------------------
WAKE_WORD = ("spark")  # Example: "hey gemini"

# ---------------------------
# 3. Speak with gTTS
# ---------------------------
def speak(text):
    """Convert text to speech using gTTS and play it."""
    print(f"Spark: {text}")
    try:
        tts = gTTS(text=text, lang="en")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            temp_file = fp.name
            tts.save(temp_file)
        playsound.playsound(temp_file)
        os.remove(temp_file)
    except Exception as e:
        print(f"TTS error: {e}")

# ---------------------------
# 4. Gemini Ask Function
# ---------------------------
def ask_gemini(prompt):
    try:
        prompt = prompt + " Keep the answer brief and start with 'Okay'. if asked for weather reply in breif one line text. Reject slangs gracefully."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I had trouble processing that."

# ---------------------------
# 5. Background Listening Callback
# ---------------------------
def callback(recognizer, audio):
    try:
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")

        if WAKE_WORD and not query.lower().startswith(WAKE_WORD):
            return
        if WAKE_WORD:
            query = query[len(WAKE_WORD):].strip()

        if query.lower().strip() in ["quit", "exit", "stop", "bye", "that's all for now","that's all"]:
            speak("Goodbye!")
            os._exit(0)

        # --- Weather detection ---
        if "weather" in query.lower():
            q_lower = query.lower()
            if " in " in q_lower:
                city = query.split(" in ", 1)[1].strip().title()
            elif "at" in q_lower:
                city = query.split("at", 1)[1].strip().title()
            else:
                speak("Okay. Please tell me the city name for the weather.")
                return

            reply = get_weather(city)
        else:
            # --- Normal Gemini flow ---
            reply = ask_gemini(query)

        speak(reply)

    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(f"Speech Recognition API error: {e}")
    except Exception as e:
        print(f"Callback error: {e}")


# ---------------------------
# 6. Main Program
# ---------------------------
speak("Hello i am your assistant Spark you can ask me any questions")
if __name__ == "__main__":
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)

    print("🎙 Listening in background... say something!")
    stop_listening = r.listen_in_background(mic, callback)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        speak("Stopping now. See you soon. Goodbye!")
