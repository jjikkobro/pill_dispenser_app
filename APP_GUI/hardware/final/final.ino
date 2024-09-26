#include <Wire.h>
#include <Adafruit_MLX90614.h>

int ENA = 2; // 환기 팬 전원선
int IN1 = 3; // 환기 팬 작동1
int IN2 = 4; // 환기 팬 작동2
bool initialRun = true; // 처음 1초 동안 255로 돌았는지 확인하는 변수

// 모터 1 핀 설정
int PUL1 = 7;  // 모터 1의 Pulse 핀
int DIR1 = 6;  // 모터 1의 Direction 핀
int ENA1 = 5;  // 모터 1의 Enable 핀

// 모터 2 핀 설정
int PUL2 = 10;  // 모터 2의 Pulse 핀
int DIR2 = 9;   // 모터 2의 Direction 핀
int ENA2 = 8;   // 모터 2의 Enable 핀

// 모터 3 핀 설정
int PUL3 = 13;  // 모터 3의 Pulse 핀
int DIR3 = 12;  // 모터 3의 Direction 핀
int ENA3 = 11;  // 모터 3의 Enable 핀

const float stepAngle = 1.8;  // 모터의 기본 스텝 각도 (1.8도 모터)
const int microsteps = 1;  // 마이크로스텝 설정을 기본 풀 스텝으로 설정
const int stepsPerRevolution = 360 / stepAngle;  // 풀 스텝 모드에서 1회전당 실제 스텝 수
const int stepsPer45Degrees = 180 / stepAngle;  // 45도 회전에 필요한 스텝 수 (풀 스텝 기준)
const int stepsPer10Degrees = 90 / stepAngle;  // 10도 회전에 필요한 스텝 수 (풀 스텝 기준)
const int stepsPer5Degrees = 89 / stepAngle;  // 5도 회전에 필요한 스텝 수 (풀 스텝 기준)

void rotateMotor(bool clockwise, int steps, int PUL, int DIR, int ENA) {
  digitalWrite(ENA, HIGH);  // 모터 활성화
  digitalWrite(DIR, clockwise ? LOW : HIGH);  // 방향 설정 (시계 방향 또는 반시계 방향)

  for (int i = 0; i < steps; i++) {
    digitalWrite(PUL, HIGH);
    delayMicroseconds(700);  // 속도를 조정하려면 이 값을 변경합니다.
    digitalWrite(PUL, LOW);
    delayMicroseconds(700);  // 속도를 조정하려면 이 값을 변경합니다.
  }
}

// MLX90614 객체 생성
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

void setup() {
  // 시리얼 모니터 시작
  Serial.begin(9600);

  // MLX90614 센서 초기화
  if (!mlx.begin()) {
    Serial.println("Error connecting to MLX90614 sensor. Check your wiring!");
    while (1);
  }

  // 타이머 설정 (ENA 핀 PWM 주파수 증가)
  TCCR3B = TCCR3B & 0b11111000 | 0x01;  // TCCR2B => 타이머2, TCCR3B => 타이머3

  // 환기모터 제어 핀을 출력 모드로 설정
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // 환기모터 방향 설정 (기본: IN1 HIGH, IN2 LOW -> 한 방향 회전)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // 모터 1 핀 모드 설정
  pinMode(PUL1, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(ENA1, OUTPUT);
  
  // 모터 2 핀 모드 설정
  pinMode(PUL2, OUTPUT);
  pinMode(DIR2, OUTPUT);
  pinMode(ENA2, OUTPUT);
  
  // 모터 3 핀 모드 설정
  pinMode(PUL3, OUTPUT);
  pinMode(DIR3, OUTPUT);
  pinMode(ENA3, OUTPUT);
}

void loop() {
  // 물체 온도 측정
  float objectTemp = mlx.readObjectTempC();
  
  // 주변 온도 측정
  float ambientTemp = mlx.readAmbientTempC();

 
  // 물체 온도에 따른 PWM 설정 (기본값 100, 0.5도 오를 때마다 PWM 20씩 증가)
  int pwmValue = 100; // 기본값 100

  if (!isnan(objectTemp)) {
    if (objectTemp > 35) {
      // Object Temperature가 35도를 초과하면 PWM을 255로 설정
      pwmValue = 255;
    } else if (objectTemp > 28) {
      // 온도가 28도를 초과하면 정상적인 PWM 계산
      pwmValue = 100 + (int)((objectTemp - 28) * 40);  // 0.5도당 20씩 증가 -> 1도당 40씩 증가
      if (pwmValue > 255) {
        pwmValue = 255;  // 최대값 제한
      }
    }
  } else {
    // 온도가 NaN일 때는 PWM을 255로 설정
    pwmValue = 255;
  }

  // 처음 1초 동안만 PWM 255로 모터를 회전
  if (initialRun) {
    analogWrite(ENA, 255);  // 1초 동안 최대 속도로 모터 회전
    delay(1000);            // 1초 대기
    initialRun = false;      // 처음 실행 완료 플래그 설정
  }

  // 그 이후에는 물체 온도에 따라 계산된 pwmValue로 계속 모터 회전
  analogWrite(ENA, pwmValue);

  for(int i=0;i<10;i++){
    if (Serial.available() > 0) {  // 시리얼 입력이 있는지 확인
      //char input = Serial.read();  // 입력된 문자 읽기
      int input = Serial.read()-'0';

      if (input == 1) {
        // 1번 모터 회전
        rotateMotor(true, stepsPer45Degrees, PUL1, DIR1, ENA1);  // 1번 모터 시계 방향으로 45도 회전
        delay(500);
        rotateMotor(false, stepsPer10Degrees, PUL1, DIR1, ENA1);  // 1번 모터 반시계 방향으로 10도 회전
        delay(500);
        rotateMotor(true, stepsPer5Degrees, PUL1, DIR1, ENA1);  // 1번 모터 시계 방향으로 5도 회전
      } 
      else if (input == 2) {
        // 2번 모터 회전
        rotateMotor(true, stepsPer45Degrees, PUL2, DIR2, ENA2);  // 2번 모터 시계 방향으로 45도 회전
        delay(500);
        rotateMotor(false, stepsPer10Degrees, PUL2, DIR2, ENA2);  // 2번 모터 반시계 방향으로 10도 회전
        delay(500);
        rotateMotor(true, stepsPer5Degrees, PUL2, DIR2, ENA2);  // 2번 모터 시계 방향으로 5도 회전
      } 
      else if (input == 3) {
        // 3번 모터 회전
        rotateMotor(true, stepsPer45Degrees, PUL3, DIR3, ENA3);  // 3번 모터 시계 방향으로 45도 회전
        delay(500);
        rotateMotor(false, stepsPer10Degrees, PUL3, DIR3, ENA3);  // 3번 모터 반시계 방향으로 10도 회전
        delay(500);
        rotateMotor(true, stepsPer5Degrees, PUL3, DIR3, ENA3);  // 3번 모터 시계 방향으로 5도 회전
      }
    }
  }
}
  //digitalWrite(ENA, LOW);  // 모터 비활성화
  
  
