from socket import * # 소켓 통신 모듈
from pyfirmata import Arduino, util # 아두이노 제어 모듈

import pygame # 음성 재생용 모듈
import MySQLdb #DB 모듈
import time # 시간 모듈
import serial  #시리얼통신용 모듈
import functools # 데이터 정제용 모듈 (문자열 자르기)
import operator # 데이터 정제용 모듈 (문자열 자르기)

host = "192.168.43.140" # 서버 IP
port = 8000 # 서버 포트번호
 
db = MySQLdb.connect("localhost", "root", "raspberry", "Companion_plant") # 서버, 사용자, DB 비밀번호, DB 이름
curs = db.cursor() #

serial_port = serial.Serial("/dev/ttyACM0", "57600") # 사용할 직렬 포트

board = Arduino("/dev/ttyACM0") # 아두이노

global first_led_color
first_led_color = 0
global second_led_color
second_led_color = 0

global first_plant_voice
first_plant_voice = 0
global second_plant_voice
second_plant_voice = 0

def SaveSensorValue(sensor_name , sensor_value, plant_number): # 매개변수 - 업데이트할 센서, 업데이트할 값, 업데이트할 식물번호
    sql = "UPDATE Sensor_value SET ? = ! WHERE Plant_number = @"
    sensor_value = str(sensor_value)
    sensor_value = sensor_value.replace("'","")
    sensor_value = sensor_value.replace("\\","")
    sensor_value = sensor_value.replace("b","")
    sensor_value = sensor_value.replace("r","")
    sensor_value = sensor_value.replace("n","")
    sql = sql.replace("?",str(sensor_name))
    sql = sql.replace("!",str(sensor_value))
    sql = sql.replace("@",str(plant_number))
    curs.execute(sql) # curs 객체에 sql문 실행
    db.commit() # 트랜잭션 종료

def SelectPlant(): # 식물 이름 리스트 형태로 저장
    sql = "SELECT Name FROM Plant_number;"
    curs.execute(sql)
    tuple_value = curs.fetchmany(2)
    db.commit()
    
    return tuple_value

def SelectValue(sensor_value,select_plant):
        select_plant = "'" + select_plant
        select_plant = select_plant + "'"
        sql = "SELECT ? FROM Sensor_value INNER JOIN Plant_number ON Sensor_value.Plant_number = Plant_number.Number WHERE Name = !"
        sql = sql.replace("?",sensor_value)
        sql = sql.replace("!",select_plant)
        curs.execute(sql) # sql문 실행
        tuple_value = curs.fetchone() # 조회된 결과로부터 데이터 1개를 반환한 뒤 변수에 저장
        db.commit() # 트랜잭션 종료
        select_value = str(tuple_value[0])
        
        return select_value # 센서값 반환
    
def PlantVoice(sensor_value, over_value, little_value, over_sound_file, little_sound_file, good_sound_file):
     if (sensor_value > over_value):
          sound_play = over_sound_file
          pygame.init()
          pygame.mixer.init()
          pygame.mixer.music.load(sound_play)
          pygame.mixer.music.play()
     elif(sensor_value < little_value):
          sound_play = little_sound_file
          pygame.init()
          pygame.mixer.init()
          pygame.mixer.music.load(sound_play)
          pygame.mixer.music.play()
     else:
          sound_play = good_sound_file
          pygame.init()
          pygame.mixer.init()
          pygame.mixer.music.load(sound_play)
          pygame.mixer.music.play()

def PlantControl(pin,state):
    board.digital[pin].write(state)
    
def RefineTuple(refine_tuple):
    complete_refine = str(functools.reduce(operator.add, (refine_tuple)))
    complete_refine = complete_refine.replace("(","")
    complete_refine = complete_refine.replace(")","")
    complete_refine = complete_refine.replace("'","")
    complete_refine = complete_refine.replace(" ","")
    complete_refine = complete_refine.replace(",","")
    
    return complete_refine

serverSocket = socket(AF_INET, SOCK_STREAM) # IPv4, TCP 소켓
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # 소켓을 1초에 한번씩 재사용 가능하도록 변경
serverSocket.bind((host,port)) # bind로 아이피와 포트번호 묶기
serverSocket.listen(5) # 최대 5개의 연결을 대기열에 넣는다

PlantControl(3,1) # LED 적색 끄기
PlantControl(4,1) # LED 녹색 끄기
PlantControl(5,1) # LED 청색 끄기

PlantControl(6,1) # 물펌프 + 작동 중지
PlantControl(7,1) # 물펌프 - 작동 중지

PlantControl(9,1) # LED 적색 끄기
PlantControl(10,1) # LED 녹색 끄기
PlantControl(11,1) # LED 청색 끄기

PlantControl(12,1) # 물펌프 + 작동 중지
PlantControl(13,1) # 물펌프 - 작동 중지

print("접속 대기")

while True:
    try:
        ReceiveWaterValue1 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장
        ReceiveSunValue1 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장
        ReceiveTempValue1 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장
        ReceiveWaterValue2 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장
        ReceiveSunValue2 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장
        ReceiveTempValue2 = serial_port.readline() # 연결된 포트에서 한줄 읽어서 변수에 저장

        SaveSensorValue("Water_value", ReceiveWaterValue1, 1)
        SaveSensorValue("Sun_value", ReceiveSunValue1, 1)
        SaveSensorValue("Temp_value", ReceiveTempValue1, 1)
        SaveSensorValue("Water_value", ReceiveWaterValue2, 2)
        SaveSensorValue("Sun_value", ReceiveSunValue2, 2)
        SaveSensorValue("Temp_value", ReceiveTempValue2, 2)
        
        connectionSocket,addr = serverSocket.accept() # 연결에서 데이터를 보내고 받을 수 있는 새로운 소켓 객체, 소켓에 바인드된 주소 -> 두 개의 값을 받음

        recived_data = connectionSocket.recv(1024) # 1024바이트 크기만큼 데이터를 받아서 변수안에 저장

        data = recived_data.decode("utf-8") # utf-8 형태로 디코딩

        data = str(data) # 문자열로 형변환 후 변수에 저장
        
        print(data)
        
        plant_name = SelectPlant()
        first_plant = RefineTuple(plant_name[0])
        second_plant = RefineTuple(plant_name[1])

        if "서버연결" in data:
            tuple_data = SelectPlant()
            send_data = str(functools.reduce(operator.add, (tuple_data)))
            send_data = send_data.replace("(","")
            send_data = send_data.replace(")","")
            send_data = send_data.replace("'","")
            send_data = send_data.replace(" ","")
            send_data = bytes(send_data,"utf-8")
            connectionSocket.send(send_data)
        elif "식물상태확인" in data:
            selected_plant = data.lstrip("식물상태확인")
            selected_plant = selected_plant.rstrip()
            send_data = ""
            define_sun = float(SelectValue("Sun_value",selected_plant))
            define_sun = define_sun / 1000 * 100
            define_sun = round(define_sun)
            send_data = send_data + str(define_sun)
            send_data = send_data + "%,"
            define_water = float(SelectValue("Water_value",selected_plant))
            define_water = abs(define_water / 1023 * 100 - 100) # 절대값
            define_water = round(define_water)
            send_data = send_data + str(define_water)
            send_data = send_data + "%,"
            define_temp = float(SelectValue("Temp_value",selected_plant))
            define_temp = round(define_temp)
            send_data = send_data + str(define_temp)
            send_data = send_data + "°C"
            send_data = bytes(send_data,"utf-8")
            connectionSocket.send(send_data)
            
            if first_plant in data:
                first_plant_voice = first_plant_voice + 1
                if(first_plant_voice == 0):
                    PlantVoice(define_temp, 28, 19, "/home/pi/MinSang/MinSang_High_Temp.ogg", "/home/pi/MinSang/MinSang_Low_Temp.ogg", "/home/pi/MinSang/MinSang_Good_2.ogg")
                elif(first_plant_voice == 1):
                    PlantVoice(define_sun, 70, 30, "/home/pi/MinSang/MinSang_High_Light.ogg", "/home/pi/MinSang/MinSang_Low_Light.ogg", "/home/pi/MinSang/MinSang_Good_0.ogg")
                elif(first_plant_voice == 2):
                    PlantVoice(define_water, 70, 40, "/home/pi/MinSang/MinSang_Over_Water.ogg", "/home/pi/MinSang/MinSang_Little_Water.ogg", "/home/pi/MinSang/MinSang_Good_1.ogg")
                else:
                    first_plant_voice = 0
                    PlantVoice(define_temp, 28, 19, "/home/pi/MinSang/MinSang_High_Temp.ogg", "/home/pi/MinSang/MinSang_Low_Temp.ogg", "/home/pi/MinSang/MinSang_Good_2.ogg")  
            elif second_plant in data:
                second_plant_voice = second_plant_voice + 1
                if(second_plant_voice == 0):
                    PlantVoice(define_temp, 28, 19, "/home/pi/Ara/Ara_High_Temp.ogg", "/home/pi/Ara/Ara_Low_Temp.ogg", "/home/pi/Ara/Ara_Good_2.ogg")
                elif(second_plant_voice == 1):
                    PlantVoice(define_sun, 70, 30, "/home/pi/Ara/Ara_High_Light.ogg", "/home/pi/Ara/Ara_Low_Light.ogg", "/home/pi/Ara/Ara_Good_0.ogg")
                elif(second_plant_voice == 2):
                    PlantVoice(define_water, 70, 40, "/home/pi/Ara/Ara_Over_Water.ogg", "/home/pi/Ara/Ara_Little_Water.ogg", "/home/pi/Ara/Ara_Good_1.ogg")
                else:
                    second_plant_voice = 0
                    PlantVoice(define_temp, 28, 19, "/home/pi/Ara/Ara_High_Temp.ogg", "/home/pi/Ara/Ara_Low_Temp.ogg", "/home/pi/Ara/Ara_Good_2.ogg")
        elif "물주기" in data:
            if first_plant in data:
                PlantControl(6,0) # 물펌프 + 작동 시작
                time.sleep(3) # 3초간 기다리기
                PlantControl(6,1) # 물펌프 + 작동 중지
                PlantControl(7,1) # 물펌프 - 작동 중지
            elif second_plant in data:
                PlantControl(12,0) # 물펌프 + 작동 시작
                time.sleep(3) # 3초간 기다리기
                PlantControl(12,1) # 물펌프 + 작동 중지
                PlantControl(13,1) # 물펌프 - 작동 중지                
        elif "빛조정" in data:
            if first_plant in data:
                first_led_color =  first_led_color + 1
                if(first_led_color == 0): # LED 작동 중지
                    PlantControl(3,1) # LED 적색 끄기 
                    PlantControl(4,1) # LED 녹색 끄기
                    PlantControl(5,1) # LED 청색 끄기
                elif(first_led_color == 1): # LED 자주색 작동
                    PlantControl(3,0) # LED 적색 끄기
                    PlantControl(4,1) # LED 녹색 끄기
                    PlantControl(5,0) # LED 청색 끄기
                elif(first_led_color == 2):
                    PlantControl(3,0) # LED 적색 끄기
                    PlantControl(4,1) # LED 녹색 끄기
                    PlantControl(5,1) # LED 청색 끄기
                elif(first_led_color == 3):
                    PlantControl(3,1) # LED 적색 끄기
                    PlantControl(4,1) # LED 녹색 끄기
                    PlantControl(5,0) # LED 청색 끄기
                elif(first_led_color > 3): # LED 작동 중지
                    first_led_color = 0
                    PlantControl(3,1) # LED 적색 끄기
                    PlantControl(4,1) # LED 녹색 끄기
                    PlantControl(5,1) # LED 청색 끄기
            elif second_plant in data:
                second_led_color =  second_led_color + 1
                if(second_led_color == 0): # LED 작동 중지
                    PlantControl(9,1) # LED 적색 끄기 
                    PlantControl(10,1) # LED 녹색 끄기
                    PlantControl(11,1) # LED 청색 끄기
                elif(second_led_color == 1): # LED 자주색 작동
                    PlantControl(9,0) # LED 적색 끄기
                    PlantControl(10,1) # LED 녹색 끄기
                    PlantControl(11,0) # LED 청색 끄기
                elif(second_led_color == 2):
                    PlantControl(9,0) # LED 적색 끄기
                    PlantControl(10,1) # LED 녹색 끄기
                    PlantControl(11,1) # LED 청색 끄기
                elif(second_led_color == 3):
                    PlantControl(9,1) # LED 적색 끄기
                    PlantControl(10,1) # LED 녹색 끄기
                    PlantControl(11,0) # LED 청색 끄기
                elif(second_led_color > 3): # LED 작동 중지
                    second_led_color = 0
                    PlantControl(9,1) # LED 적색 끄기
                    PlantControl(10,1) # LED 녹색 끄기
                    PlantControl(11,1) # LED 청색 끄기
        else:
            send_data = "오류"
            send_data = bytes(send_data,"utf-8")
            connectionSocket.send(send_data)

    except KeyboardInterrupt:
        break

connectionSocket.close()
serverSocket.close() # 소켓 닫기
port.close() # 포트 닫기
db.close() # DB 닫기

print("접속 종료") 