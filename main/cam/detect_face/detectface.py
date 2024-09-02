import cv2
import torch
from ultralytics import YOLO

# 모델 로드
model = YOLO('/home/hongpi123/project/pill_dispenser_app/main/cam/best.pt')

# 클래스 이름 설정
class_names = ['person']

# 비디오 캡처 객체 정의
cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 사용, 다른 카메라를 사용할 경우 번호를 변경

# 카메라가 제대로 열렸는지 확인
if not cap.isOpened():
    print("Error: 비디오 스트림을 열 수 없습니다.")
    exit()

# 프레임 해상도 설정 (필요에 따라 조정)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 노출 값 설정 (필요에 따라 조정)
exposure_value = -4
cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)

while True:
    # 프레임을 하나씩 캡처
    ret, frame = cap.read()
    if not ret:
        print("Error: 프레임을 읽을 수 없습니다.")
        break

    # 모델을 사용하여 전체 프레임에서 객체 감지
    results = model(frame)

    # 결과 처리
    for result in results:
        boxes = result.boxes  # 바운딩 박스 추출
        for box in boxes:
            # 바운딩 박스의 좌표 가져오기
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            conf = box.conf.item()  # 신뢰도 점수
            cls = int(box.cls)  # 클래스 인덱스 (int로 변환하여 사용)

            # 신뢰도 점수가 0.7 이상인 경우에만 바운딩 박스 그리기
            if conf > 0.7:
                label = f"{class_names[cls]}: {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # 객체가 인식되었음을 출력
                print("객체가 인식되었습니다")

    # 결과 프레임 표시
    cv2.imshow('Mask Detection', frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 모든 작업이 끝나면 캡처 해제
cap.release()
cv2.destroyAllWindows()

