import serial
import pymysql
from pymysql import cursors
from dotenv import dotenv_values
from ast import literal_eval

env = dotenv_values()
db_config = literal_eval(env['db_config'])

def get_cursor(conn):
    return conn.cursor(cursors.DictCursor)

def connect_to_database():
    return pymysql.connect(**db_config)
    
def get_data(curs, user_id):
    curs.execute(f"select user_id, medicine, container, dosing_time, finished, repetition from notes_note where user_id={user_id}")
    rows = curs.fetchall()
    print(rows)
    return rows

def connect_to_arduino():
    return serial.Serial('/dev/ttyACM0', 9600, timeout=.1)

def serial_send(ser, number):
    if number == 1:
        ser.write(b'1')    
    elif number == 2:
        ser.write(b'2')
    elif number == 3:
        ser.write(b'3')
    return True
    