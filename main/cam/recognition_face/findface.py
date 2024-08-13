import cv2
import numpy as np

# LBPH 얼굴 인식기 생성 및 학습된 모델 로드
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('/home/hongpi123/Desktop/project/pill_dispenser_app/main/cam/recognition_face/trainer/trainer.yml')

# Haar Cascade 파일 경로 설정
cascadePath = '/home/hongpi123/Desktop/project/pill_dispenser_app/main/cam/recognition_face/haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath)

# 글꼴 설정
font = cv2.FONT_HERSHEY_SIMPLEX

# 사용자 이름 목록 (이름은 필요에 따라 추가/수정하세요)
names = ['hong']  # ID 순서에 맞게 수정

# 카메라 설정
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# 최소 얼굴 크기 설정
minW = 0.1 * cam.get(cv2.CAP_PROP_FRAME_WIDTH)
minH = 0.1 * cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 얼굴 검출
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(int(minW), int(minH))
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 얼굴 인식 및 신뢰도 계산
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        # 신뢰도가 55% 미만인 경우 이름 표시, 그렇지 않으면 "unknown" 표시
        if confidence < 55:
            id = names[id]
        else:
            id = "unknown"
        
        confidence_text = "  {0}%".format(round(100 - confidence))

        # 텍스트 표시
        cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence_text), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
    
    # 실시간 화면 출력
    cv2.imshow('camera', img)

    # 종료 조건: 'q' 키를 누르면 종료
    if cv2.waitKey(1) > 0:
        break

# 프로그램 종료 및 리소스 해제
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
