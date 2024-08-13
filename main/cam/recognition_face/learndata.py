import cv2
import numpy as np
from PIL import Image
import os

# Haar Cascade 파일 경로 설정 (절대 경로)
cascade_path = '/home/hongpi123/Desktop/project/pill_dispenser_app/main/cam/recognition_face/haarcascade_frontalface_default.xml'
detector = cv2.CascadeClassifier(cascade_path)

# LBPH 얼굴 인식기 생성
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 데이터셋 경로
path = 'dataset'

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples = []
    ids = []
    
    for imagePath in imagePaths:
        # 흑백 변환
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')

        # 파일명에서 ID 추출
        # 예시: User.hong.1.jpg -> 'hong' 부분을 추출
        id = os.path.split(imagePath)[-1].split(".")[1]  # 이 부분을 수정하여 문자열 ID를 그대로 가져옵니다.
        
        # 얼굴 샘플
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)  # 문자열 ID를 그대로 추가

    return faceSamples, ids

print('\n [INFO] Training faces. It will take a few seconds. Wait ...')
faces, ids = getImagesAndLabels(path)

# 학습 전 문자열 ID를 숫자로 인코딩 (LabelEncoder 사용)
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
encoded_ids = label_encoder.fit_transform(ids)

# 얼굴 인식기 학습
recognizer.train(faces, np.array(encoded_ids))

# 학습된 모델 저장
if not os.path.exists('trainer'):
    os.makedirs('trainer')
recognizer.write('trainer/trainer.yml')

print('\n [INFO] {0} faces trained. Exiting Program'.format(len(np.unique(encoded_ids))))
