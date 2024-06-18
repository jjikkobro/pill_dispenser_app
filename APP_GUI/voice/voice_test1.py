import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

def record(filename, duration, samplerate=44100):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait() 
    write(filename, samplerate, audio)
    print(f"Audio recording saved as {filename}")
    
if __name__=="__main__":
    record("test.wav", 5)