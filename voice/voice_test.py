import requests
from dotenv import dotenv_values
import azure.cognitiveservices.speech as speechsdk


class Pill_Genine():
    
    def __init__(self):
        env = dotenv_values()
        self.gpt_4o_key = env['gpt_4o_apikey']
        self.gpt_4o_endpoint = env['gpt_4o_endpoint']
        
    def call_gpt(self, messages):
        client = OpenAI(
            api_key= self.gpt_4o_apikey
        )
        response = client.chat.completions.create(
          model="gpt-3.5-turbo-0125",
          response_format={ "type": "json_object" },
          messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": "Who won the world series in 2020?"}
          ]
        )
        print(response.choices[0].message.content)