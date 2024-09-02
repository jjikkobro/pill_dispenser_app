import pymysql
from pymysql import cursors
import serial
import time
from datetime import datetime
import requests
import keyboard

weekdays = ['mon','tue', 'wed', 'thu', 'fri', 'sat', 'sun']
# MySQL 데이터베이스 연결 함수
def connect_to_database():
    return pymysql.connect(
        host = "172.190.90.75",
        user = "pill",
        password = "qwer3249@",
        database = "pill_dispenser",
        charset = "utf8",
        autocommit = True
    )
    
def get_user_id(curs, name):
    curs.execute(f"select id from auth_user where username='{name}'")
    user_id = curs.fetchone()['id']
    print(user_id)
    return user_id

def get_data(curs, user_id):
    curs.execute(f"select user_id, medicine, container, dosing_time, finished, `repeat` from notes_note where user_id={user_id}")
    rows = curs.fetchall()
    print(rows)
    return rows
    

def check_and_send_signal(curs ,rows):
    print("신호 확인 및 전송 시작")
    while True:     
        if keyboard.is_pressed('q'):
            rows = get_data(curs, user_id)
            print(rows)
            print('Get new data')
            
        current_time = datetime.now().strftime('%H:%M')
        current_date = weekdays[datetime.now().weekday()]
        
        #print(f"현재 시간: {current_time}")
        for row in rows:
            user_id, medicine, container, dosing_time, finished, repeat = row.values()
            if ('daily' in repeat) or current_date in repeat:
                if str(dosing_time).rstrip(':00') == str(current_time) and finished == 0:    
                    print(f"사용자: {user_id}, 약 이름: {medicine}, 약 통 번호: {container}, 시간: {dosing_time}")
                    curs.execute(f"UPDATE notes_note set finished=1 where container={container}")
                    row['finished'] = 1
                    ser.write(b'1') #아두이노로 신호 전송
                else:
                    continue
            else:
                print('오늘이 아님', repeat)
                continue
    print("신호 확인 및 전송 완료")

if __name__ == "__main__":
    # MySQL 데이터베이스에 연결
    conn = connect_to_database()
    name = "홍석민"
    
    cursor = conn.cursor(cursors.DictCursor)
    user_id = get_user_id(cursor, name)
    
    rows = get_data(cursor, user_id)
    # 시리얼 포트와 통신 속도 설정
    ser = serial.Serial('/dev/ttyACM0', 9600)  # '/dev/ttyUSB0'는 아두이노가 연결된 포트
    time.sleep(2)  # 시리얼 통신 안정화 시간
    check_and_send_signal(cursor, rows)
    # 데이터베이스 연결 종료
    conn.close()
