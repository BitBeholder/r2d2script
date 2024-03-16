import pyaudio
import wave

def record_audio(audio_filename, is_recording):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    sample_rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk)

    frames = []

    print("Audio recording started.")

    # Record until is_recording is cleared
    while is_recording.is_set():
        data = stream.read(chunk)
        frames.append(data)
        
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Audio recording stopped and file saved.")
    print(f"Saving audio file to: {audio_filename}")
