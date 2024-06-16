import pymysql
from dotenv import dotenv_values
import django
from ast import literal_eval
from django.conf import settings
from django.contrib.auth.hashers import check_password
import os

if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.PBKDF2PasswordHasher',
            'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
            'django.contrib.auth.hashers.Argon2PasswordHasher',
            'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        ],
    )

# Django 초기화
django.setup()

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', )
# django.setup()

env = dotenv_values()
db_config = literal_eval(env['db_config'])

def connect_to_database(db_config):
    return pymysql.connect(**db_config)

def login(conn, username, password):
    try:
        with conn.cursor() as cursor:
            sql = "SELECT password FROM auth_user WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            
            if result:
                stored_password = result[0]
                if check_password(password, stored_password):
                    sql = "SELECT id FROM auth_user WHERE username=%s"
                    cursor.execute(sql, (username,))
                    user_id = cursor.fetchone()[0]
                    return user_id
                else:
                    return False
            else:
                return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def main(username, password):
    conn = connect_to_database(db_config)
    user_id = login(conn, username, password)
    if user_id:
        conn.close()
        return {"code":"success","message":"Login success.","user_id":user_id}
    else:
        conn.close()
        return {"code":"fail","message":"Login failed. Please try again."}
    