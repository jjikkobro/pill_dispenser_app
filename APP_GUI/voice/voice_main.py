import requests
from dotenv import dotenv_values
from ast import literal_eval
import os
import pymysql
import simpleaudio as sa
from . import make_mp3
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import re
# import simpleaudio as sa


class Pill_Genine():
    def __init__(self):
      env = dotenv_values()
      self.user_id = 1
      self.gpt_4o_key = env['gpt_4o_apikey']
      self.gpt_4o_endpoint = env['gpt_4o_endpoint']
      self.db_config = literal_eval(env['db_config'])
      self.base_dir = "/home/hoseo/pill_dispenser_app/APP_GUI"
      self.silence_threshold = 500
      self.silence_duration = 1
        
    def generate_chat_completion(self, messages,  temperature=0.2, max_tokens=None):
      print(self.gpt_4o_key)
      print(self.gpt_4o_endpoint)
      post_fields = {
          "messages": messages,
          "response_format":{ "type": "json_object" }
      }
      headers = {
          "Content-Type": "application/json",
          "api-key": self.gpt_4o_key,
      }
      url = self.gpt_4o_endpoint
      response = requests.post(
          url, headers=headers, json=post_fields, timeout=19)

      if response.status_code == 200:
          return response.json()["choices"][0]["message"]["content"]
      else:
          raise Exception(f"Error {response.status_code}: {response.text}")


    def message_maker(self, text, omission=None, prev_result=None, re=False):
      if not re:
        messages =[
            {"role":"system", "content":"""You are a reservation system. Follow the given instruction.
              Instructions : 
              1. You should parse 'repeatition day of week, time, name of pill, container number' from the given script. 
              2. You should parse informations as json format. 
              3. You should response name of the pill in Korean. 
              4. If there are no information in script, You should response empty string as value but keep the keys.
              5. If user says no in script, You should response this {"information":""} 
              6. container number and repetition are must be one of the below example.
              
              Example Format : {
                "information" : {
                  "medicine":"<name of the pill in Korean>" : str,
                  "container":<1|2|3> : int,
                  "repetition":"<daily|mon|tue|wed|thu|fri|sat|sun>" : str,
                  "dosing_time":"<HH:MM>" : str
                },
                "tts" : "<TTS script for confirmation in Korean converted all numbers to words>" : str, example :일 번 통에 오메가 쓰리, 월, 수, 금 오후 세시, 저장할까요?
              }
              """},
            {"role":"user","content":f"""You should follow the system instructions.
              Here is the script :
              Machine : 약 통의 번호, 이름, 반복 할 요일 과 시간을 말씀해주세요.
              User : {text}
              """}
        ]
      else:
        messages =[
            {"role":"system", "content":"""You are a reservation system. Follow the given instruction.
              Instructions : 
              1. You should keep the given result and just put added value from the script.
              2. You should parse informations as json format. 
              3. You should response name of the pill in Korean. 
              4. container number and repetition are must be one of the below example.
              
              Example Format : {
                "information" : {
                  "medicine":"<name of the pill in Korean>" : str,
                  "container":<1|2|3> : int,
                  "repetition":"<daily|mon|tue|wed|thu|fri|sat|sun>" : str,
                  "dosing_time":"<HH:MM>" : str
                },
                "tts" : "<TTS script for confirmation in Korean converted all numbers to words>" : str, example :일 번 통에 오메가 쓰리, 월, 수, 금 오후 세시, 저장할까요?
              }
              """},
            {"role":"user","content":f"""You should follow the system instructions.
              Previous Result :
              {prev_result}
              Here is the script :
              Machine : {omission}에 대한 정보가 없습니다. 다시 제공해주세요.
              User : {text}
              """}
        ]
      return messages

    def check_result(self, result):
      result['user_id'] = self.user_id      
      for key, value in result.items():
        if not value:
          return key
      
      columns = ', '.join(result.keys())
      values = ', '.join(['%s'] * len(result))
      
      return {'columns':columns, 'values':values}
      
    
    def play_mp3(self, file_name=None, text=None):
      if text:
        file_name = make_mp3.make_mp3_file(text, file_name)
        if file_name == False:
          return False
        
      wave_obj = sa.WaveObject.from_wave_file(f"{self.base_dir}/voice/tts_output/{file_name}.wav")
      play_obj = wave_obj.play()
      play_obj.wait_done()
      
    def save_to_database(self, key_value, result):
      connection = pymysql.connect(**self.db_config)
      query = f"INSERT INTO notes_note ({key_value['columns']}) VALUES ({key_value['values']})"
      with connection.cursor() as cursor:
          cursor.execute(query, list(result['information'].values()))
      connection.commit()
      connection.close()
    
    def record(self, duration, samplerate=44100):
      sd.default.device = "HK 1080 Cam"
      basedir = os.getcwd()
      output_path = os.path.join(basedir,'voice/audio_input/record.wav')
      audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
      sd.wait() 
      write(output_path, samplerate, audio)
      return output_path
    
    def recoginze(self, wav_path): 
      return make_mp3.wav_to_text(wav_path)
    
    def replace_similar_phrases(self, text):
      patterns = {
        r"일본통|일본동|일번동|일번통": "1번통",
        r"이본통|이번통|이번동|이본동": "2번통",
        r"삼번통|삼본통|삼번동|삼본동": "3번통",
        r"내일": "매일",
      }
      for pattern, replacement in patterns.items():
            text = re.sub(pattern, replacement, text)
    
      return text