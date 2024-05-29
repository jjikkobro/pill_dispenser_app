import cv2
import time 

def show_camera():
    # 카메라 모듈 활성화
    cap = cv2.VideoCapture(0)

    # 카메라가 정상적으로 열렸는지 확인
    if not cap.isOpened():
        print("Error: 카메라를 열 수 없습니다.")
        return

    while True:
        # 카메라로부터 프레임 읽기
        ret, frame = cap.read()

        # 프레임을 성공적으로 읽었는지 확인
        if not ret:
            print("Error: 프레임을 읽을 수 없습니다.")
            break

        # 프레임 출력
        cv2.imshow('Camera', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 작업 완료 후 카메라 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_camera()
