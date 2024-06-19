import os
from dotenv import dotenv_values
from ast import literal_eval
from flask import Flask, jsonify, send_file, request
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

basedir = os.getcwd()
env = dotenv_values()
speech_key = env['speech_key']
speech_region = env['speech_region']
speaker = ['']
output_folder = os.path.join('voice','tts_output')
os.makedirs(output_folder, exist_ok=True)
app = Flask(__name__)


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
        return outputPath
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                return False

def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        return f"Speech Recognition canceled: {cancellation_details.reason}"

@app.route('/recognize', methods=['POST'])
def recognize():
    text = recognize_from_microphone()
    return jsonify({'code':'success','text': text})

@app.route('/make_mp3', methods=['GET'])
def make_mp3():
    output_path = make_mp3_file()
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    else:    
        return jsonify({"code":"Error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)