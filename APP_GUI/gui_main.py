import dearpygui.dearpygui as dpg
import authenticate.auth as Auth
import static.load_static_files as load_statics
from voice.voice_main import Pill_Genine
from ast import literal_eval
from hardware import send_to_arduino as Ardu
import time
from datetime import datetime

kor_font_file = load_statics.kor_font
soundwave_gif_file = load_statics.soundwave_gif
user_id = None
dosing_data = None
conn, ser = None, None
weekdays = ['mon','tue', 'wed', 'thu', 'fri', 'sat', 'sun']

dpg.create_context()

def set_global_font(): 
    with dpg.font_registry():
        with dpg.font(kor_font_file, 20) as font1:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.bind_font(font1)
       

def open_index_page():
    with dpg.window(label="Index Page", width=800, height=600):
        dpg.add_button(label="예약 하기", callback= reservation, width=700, height=190)
        dpg.add_button(label="바로 투약", callback=give_pill, width=700, height=190)
        dpg.add_button(label="자동 투약", callback=lambda: period_dosage(), width=700, height=190)
        dpg.add_button(label="로그아웃", callback=logout)

def open_once_dosage_page():
    with dpg.window(label="바로 투약", width=800, height=600, tag="once_dosage_window"):
        dpg.add_text("어떤 통의 약을 꺼내시겠습니까?")
        with dpg.group(horizontal=True):
            dpg.add_button(label="1번 통", callback=send_serial, user_data={"command":"once","conatiner_number":1}, width=230, height=300)
            dpg.add_button(label="2번 통", callback=send_serial, user_data={"command":"once","conatiner_number":2}, width=230, height=300)
            dpg.add_button(label="3번 통", callback=send_serial, user_data={"command":"once","conatiner_number":3}, width=230, height=300)
        dpg.add_button(label="뒤로 가기", callback=lambda: return_to_index(delete_from="once"))
        
def open_period_dosage_page(rows, curs):
    with dpg.window(label="자동 투약", width=800, height=600, tag="period_dosage_window"):
        dpg.add_text("자동 투약이 활성화 되었습니다.")
        
        with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True):
            dpg.add_table_column(label="통 번호")
            dpg.add_table_column(label="약 이름")
            dpg.add_table_column(label="시간")
            dpg.add_table_column(label="반복")

            for row in rows:
                with dpg.table_row():
                    dpg.add_text(row['container'])
                    dpg.add_text(row['medicine'])
                    dpg.add_text(row['dosing_time'])
                    dpg.add_text(row['repetition'])
        with dpg.group(horizontal=True):            
            dpg.add_button(label="다시 불러오기", callback=lambda: period_dosage(is_refresh=True))
            dpg.add_button(label="끝내기", callback=lambda: return_to_index(delete_from="period"))
            
    send_serial(user_data={"command":"period","data":rows,"cursor":curs})
        
def return_to_index(delete_from):
    if delete_from == "period":
        dpg.delete_item("period_dosage_window")
    elif delete_from == "once":
        dpg.delete_item("once_dosage_window")
    open_index_page()

def period_dosage(is_refresh=None):
    global conn, ser
    if is_refresh:
        dpg.delete_item("period_dosage_window")
    else:
        dpg.delete_item("index_page")
        ser = Ardu.connect_to_arduino()
        time.sleep(2)
        conn = Ardu.connect_to_database()   
    curs = Ardu.get_cursor(conn)
    rows = Ardu.get_data(curs, user_id)
    print(rows)
    open_period_dosage_page(rows, curs)

def send_serial(user_data):
    if user_data["command"] == "once":
        container_number = user_data['container_number']
        message = b'%d' % container_number
        ser.write(message)
    
    elif user_data["command"] == "period":
        rows = user_data["data"]
        curs = user_data["curs"]
        print("신호 확인 및 전송 시작")
        while True:     
            # if button.is_pressed:
            #     rows = Ardu.get_data(curs, user_id)
            #     print(rows)
            #     print('Get new data')
                
            current_time = datetime.now().strftime('%H:%M')
            current_date = weekdays[datetime.now().weekday()]
            
            #print(f"현재 시간: {current_time}")
            for row in rows:
                user_id, medicine, container, dosing_time, finished, repetition = row.values()
                if ('daily' in repetition) or current_date in repetition:
                    if str(dosing_time).rstrip(':00') == str(current_time) and finished == 0:    
                        print(f"사용자: {user_id}, 약 이름: {medicine}, 약 통 번호: {container}, 시간: {dosing_time}")
                        curs.execute(f"UPDATE notes_note set finished=1 where container={container}")
                        row['finished'] = 1
                        ser.write(b'1') #아두이노로 신호 전송
                    else:
                        continue
                else:
                    print('오늘이 아님', repetition)
                    continue
    

def give_pill():
    dpg.delete_item("index_page")
    open_once_dosage_page()
    

def open_reservation_page():
    with dpg.window(label="예약 페이지", width=800, height=600):
        dpg.add_text("예약 중 입니다.")

def reservation():
    dpg.delete_item("index_page")
    open_reservation_page()
    Genine = Pill_Genine()

    # user_response = Genine.record()
    print("예약을 희망하시면, 컨테이너 번호, 약 이름, 반복 요일과 시간을 말씀해주세요.")
    user_response = input()

    message = Genine.message_maker(user_response)
    result = Genine.generate_chat_completion(message)

    save = False
    while(not save):
        result = literal_eval(result)
        if result['information'] == '':
            print("취소되었습니다.")
            break
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
    dpg.delete_item("reservation_page")
    open_index_page()
        
def logout(sender, app_data):
    dpg.delete_item("index_page")
    dpg.show_item("login_page")

def login(sender, app_data):
    global user_id
    username = dpg.get_value("username")
    password = dpg.get_value("password")
    
    is_user = Auth.main(username, password)
    if is_user['code']=="success":
        user_id = is_user['user_id']
        dpg.set_value("status", "Login Successful!")
        dpg.hide_item("login_page")
        open_index_page()
    else:
        dpg.set_value("status", is_user['message'])

def open_login_page():
    with dpg.window(label="Login", width=800, height=600, tag="login_page"):
        dpg.add_text("아이디와 비밀번호를 입력하세요.")
        
        dpg.add_input_text(label="아이디", tag="username")
        dpg.add_input_text(label="비밀번호", tag="password", password=True)
        
        dpg.add_button(label="로그인", callback=login)
        dpg.add_text("", tag="status")

def main():     
    set_global_font()
    open_login_page()    
    dpg.create_viewport(title='Pill_Dispenser_APP', width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
