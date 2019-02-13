import datetime
import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Ps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#관리자 프로그램 접속
ip = '192.168.0.8'
port = 4969
s.connect((ip, port))
my = 'Calculator'
s.send(my.encode('utf-8'))
print("서버 접속")

#압력 인식 프로그램 서버
port_p = 4971
Ps.bind(('192.168.0.10', port_p))
Ps.listen(1)
Parking_System, addr = Ps.accept()
print('주차장 공간 관리 프로그램 접속 완료')


class calculate:
    park_start_list={}
    for i in range(20):
        park_start_list[i+1] = None
    
    # 시작시간
    def start_time(self):
        start = datetime.datetime.now()
        start_day = start.day
        start_hour = start.hour
        start_minute = start.minute
        return (start_day, start_hour, start_minute)

    #끝난 시간
    def end_time(self):
        end = datetime.datetime.now()
        end_day = end.day
        end_hour = end.hour
        end_minute = end.minute

        return (end_day,end_hour, end_minute)

    #사용 시간
    def count_time(self, parking_num, end_day, end_hour, end_minute):

        if end_day>self.park_start_list[parking_num][1]:
            n = end_day - self.park_start_list[parking_num][0]
            end_hour = end_hour + 24*n
            
        use_hour = end_hour - self.park_start_list[parking_num][1]
        use_minute = end_minute - self.park_start_list[parking_num][2]

        if use_minute >= 1:
            final_time = use_hour + 1
        else:
            final_time = use_hour

        return final_time
    
    #요금 정산
    def final_fare(self, use_hour):
        fare = 2000
        result = fare * use_hour
        return result

    def recv_data(self, Parking_System):
        parking_num = Parking_System.recv(1024).decode('utf-8')
        information = 'carIn' + '@' + str(parking_num)
        s.send(information.encode('utf-8'))
        park_data = self.start_time()
        print(parking_num)
        self.park_start_list[parking_num] = park_data

    def send_data(self):
        Parking_System.send(parking_num. encode('utf-8'))
            

P = calculate()
while True:
  
    print("\n무인 주차장 시스템 입니다/// 시간당 2000원 // 1분 초과해도 시간 단위로 계산 됩니다.")
    cmd = int(input("1.요금조회------2.요금 정산---------"))
    
    threading.Thread(target = P.recv_data, args = (Parking_System,)).start()
    if cmd == 1:
        park_end_day,park_end_hour, park_end_minute = P.end_time()
        parking_num = input("주차 자리를 입력해주세요: ")
        try:
            user_time = P.count_time(parking_num, park_end_day, park_end_hour, park_end_minute)
            money = P.final_fare(user_time)
            print(parking_num + " 번 자리의 현재 요금은 " + str(money) +"입니다.")
        except:
            print("빈 주차 자리입니다.")

    #주차 요금 정산
    elif cmd == 2:
        park_end_day,park_end_hour, park_end_minute = P.end_time()
        parking_num = input("주차 자리를 입력해주세요: ")
        try:
            user_time = P.count_time(parking_num, park_end_day, park_end_hour, park_end_minute)
            money = P.final_fare(user_time)
            print(parking_num + " 번 자리의 현재 요금은 " + str(money) +"입니다.")
            pay = int(input("내실 요금을 입력하세요"))
            if pay == money:
                data = 'parkingFee' + '@' + parking_num + '@' + str(money)
                print('정산 대기중')
                
                s.send(data. encode('utf-8'))
                print("정산완료 하였습니다, 감사합니다.")

                P.send_data()
               
            else:
                print("정산 실패 하였습니다. 다시 한번 확인해 주세요")
        except:
            print("빈 주차 자리입니다.")
