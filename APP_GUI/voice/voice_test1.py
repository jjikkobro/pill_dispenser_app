from ast import literal_eval
from pill_dispenser_app.APP_GUI.voice.voice_main import Pill_Genine

def main():
    Genine = Pill_Genine()

    # user_response = Genine.record()
    print("예약을 희망하시면, ")
    user_response = input()

    message = Genine.message_maker(user_response)
    result = Genine.generate_chat_completion(message)

    save = False
    while(not save):
        result = literal_eval(result)
        key_value = Genine.check_result(result['information'])
        if type(key_value) == str:
            question = Genine.play_mp3(file_name=key_value)
            print(key_value+'에 대한 정보가 없습니다. 다시 말씀 해주세요.')
            user_response = input()
            message = Genine.message_maker(user_response, omission=key_value, prev_result=result['information'], re=True)
            result = Genine.generate_chat_completion(message)        
        else:
            print(result)
            question = Genine.play_mp3(text=result['tts'], file_name="final")
            Genine.save_to_database(key_value, result)
            print("저장되었습니다.")
            save = True
        
    

    

