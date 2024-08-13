import cv2
import os

# Haar Cascade classifier 초기화
faceCascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

# Video capture 초기화
capture = cv2.VideoCapture(0)  # 카메라 인덱스 0번 사용
if not capture.isOpened():
    print("[ERROR] Camera could not be opened. Exiting...")
    exit()

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# 사용자 ID 입력
face_id = input('\n enter user id and press <return> ==> ')
print("\n [INFO] Initializing face capture. Look at the camera and wait ...")

# dataset 폴더 생성(없는 경우)
if not os.path.exists('dataset'):
    os.makedirs('dataset')

# 기존 데이터셋 폴더에서 해당 사용자의 이미지를 확인하여 중복되지 않게 설정
count = len([f for f in os.listdir('dataset') if f.startswith(f'User.{face_id}.')])

# 영상 처리 및 출력
while True: 
    ret, frame = capture.read()  # 프레임 캡처
    if not ret:
        print("[ERROR] Failed to capture frame. Exiting...")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 프레임을 흑백으로 변환
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(20, 20)
    )

    # 얼굴이 인식된 경우에만 이미지를 저장
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            count += 1
            cv2.imwrite(f"dataset/User.{face_id}.{count}.jpg", gray[y:y+h, x:x+w])
            print(f"[INFO] Saved dataset/User.{face_id}.{count}.jpg")
    else:
        print("[DEBUG] No faces detected.")

    # 현재 프레임을 화면에 표시
    cv2.imshow('image', frame)

    # 종료 조건: 키 입력 시 종료
    if cv2.waitKey(1) > 0:
        break

print("\n [INFO] Exiting Program and cleanup stuff")

# 메모리 해제
capture.release()
cv2.destroyAllWindows()

