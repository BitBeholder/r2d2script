import os
import cv2
import pyttsx3
import datetime
import threading
from moviepy.editor import VideoFileClip, AudioFileClip
from audio_recorder import record_audio  # Make sure this is modified to save as .wav
from chatgpt_utils import get_greeting
from voice_chatbot import capture_audio, get_chatgpt_response, speak_text

is_recording = threading.Event()

# Function to speak text in a separate thread
def speak(text):
    def _speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak).start()

def start_voice_chatbot():
    while True:  # Keep listening for commands indefinitely
        input_text = capture_audio()
        if input_text is not None:
            response_text = get_chatgpt_response(input_text)
            speak_text(response_text)
        else:
            speak_text("I didn't catch that, could you please repeat?")

def detect_motion_and_record():
    cap = cv2.VideoCapture(0)  # '0' is the default camera
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    is_motion_detected = False
    out = None
    audio_thread = None
    last_movement_time = datetime.datetime.now()

    while cap.isOpened():
        current_time = datetime.datetime.now()
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 2000:
                continue
            last_movement_time = current_time
            if not is_motion_detected:
                is_motion_detected = True

                # Set filenames
                timestamp = current_time.strftime('%Y%m%d_%H%M%S')
                audio_filename = os.path.join('recordings', f"{timestamp}.wav")
                video_filename = os.path.join('recordings', f"{timestamp}.avi")

                # Start recording audio
                is_recording.set()
                audio_thread = threading.Thread(target=record_audio, args=(audio_filename, is_recording,))
                audio_thread.start()

                # Initialize video recording
                out = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
                print(f"Motion detected: recording {video_filename}")

                # Get and speak the greeting
                greeting = get_greeting()
                print(f"ChatGPT says: {greeting}")
                speak(greeting)

                # Start a new thread for voice chatbot to not block the main thread
                chatbot_thread = threading.Thread(target=start_voice_chatbot)
                chatbot_thread.start()

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if out is not None:
            out.write(frame1)

        no_movement = (current_time - last_movement_time).seconds > 10
        esc_pressed = cv2.waitKey(1) == 27
        no_audio_captured = not is_recording.is_set()

        if no_movement or esc_pressed or no_audio_captured:
            if is_motion_detected:
                is_motion_detected = False
                is_recording.clear()
                audio_thread.join()
                out.release()
                out = None
                print("Stopped recording due to no movement, audio or ESC pressed.")

                # Combine the audio and video
                combined_filename = os.path.join('recordings', f"{timestamp}_combined.mp4")
                video_clip = VideoFileClip(video_filename)
                audio_clip = AudioFileClip(audio_filename)
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(combined_filename, codec='libx264', audio_codec='aac')

                # Optionally delete the separate audio and video files
                os.remove(video_filename)
                os.remove(audio_filename)

                if esc_pressed:
                    print("Escape key pressed, exiting.")
                    break

        frame1 = frame2
        ret, frame2 = cap.read()
        cv2.imshow("feed", frame1)

    if out is not None:
        out.release()
    cap.release()
    cv2.destroyAllWindows()

# Call the function
detect_motion_and_record()
