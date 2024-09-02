import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
from dotenv import dotenv_values
from ast import literal_eval
import azure.cognitiveservices.speech as speechsdk

basedir = os.getcwd()
env = dotenv_values()
speech_key = env['speech_key']
speech_region = env['speech_region']
speaker = ['']
output_folder = os.path.join('voice','tts_output')
os.makedirs(output_folder, exist_ok=True)


def record(duration, samplerate=44100):
    sd.default.device = (1,None)
    basedir = os.getcwd()
    output_path = os.path.join(basedir,'voice/audio_input/record.wav')
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait() 
    write(output_path, samplerate, audio)
    
def wav_to_text(input_path):
    speech_config = speechsdk.SpeechConfig(subscription="af2aff1d03384f3c87e9fb93a170b424", region="centralus")
    speech_config.speech_recognition_language="ko-KR"
    audio_config = speechsdk.AudioConfig(filename=input_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once_async().get()
    print(result.text)

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return ""

def recognize_from_microphone():
    if not speech_key or not speech_region:
        raise ValueError("Azure Speech Key and Region must be set")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language="ko-KR"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

if __name__=="__main__":
    print(wav_to_text("/home/jung/pill_dispenser_app/test.wav"))