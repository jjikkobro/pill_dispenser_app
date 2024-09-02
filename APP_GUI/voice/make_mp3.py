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

def make_mp3_file(text, file_name=None):
    speech_config = speechsdk.SpeechConfig(subscription = speech_key, region = speech_region)
    speech_config.speech_synthesis_speech_rate = '3.0'


    speech_config.speech_synthesis_voice_name= "ko-KR-JiMinNeural"
    outputPath = os.path.join(basedir,output_folder,f'{file_name}.wav')
    audio_config = speechsdk.audio.AudioOutputConfig(filename=outputPath)

    # preference
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                return False
    return file_name
                
def wav_to_text(input_path):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language="ko-KR"
    audio_config = speechsdk.AudioConfig(filename=input_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
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