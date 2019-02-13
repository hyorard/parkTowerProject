#king.py
import socket
import threading
import sys
import os
import time

class Admin:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    isSentID = False
    sortMark = '@'
    parkLot1 = None
    parkLot2 = None
    parkLot3 = None
    parkLot4 = None
    isRcvList = False
    isResSuc = False
    isRcvTime = False
    inqMonth = None
    inqDay = None
    inqLot = None
    inqTime = None
    isRcvEarning = False
    month_earning = None
    date_earning = None
    seeingMonth = None
    NonResList = None

    def __init__(self):
        self.sock.connect(('0.0.0.0' ,4970))
        #
    def run(self):

        sThread = threading.Thread(target=self.serverHandler)
        sThread.daemon = True
        sThread.start()


        while True:

            if self.isSentID == False:
                self.sendID()
            try:
                serverMsg = self.sock.recv(1024)
            except:
                break
            serverMsg = str(serverMsg,'utf-8')
            serverMsg = serverMsg.split(self.sortMark)
            MsgHeader = serverMsg[0]


            if MsgHeader == 'NonResList':
                self.NonResList = serverMsg[1]



            if MsgHeader == 'ResList':      #예약 리스트
                self.parkLot1 = serverMsg[1]
                self.parkLot2 = serverMsg[2]
                self.parkLot3 = serverMsg[3]
                self.parkLot4 = serverMsg[4]
                self.isRcvList = True

            elif MsgHeader == 'ResSuc':     #예약 성공 시그널
                self.isResSuc = True
                ACode = serverMsg[1]
                print("발급받은 인증코드는 " + ACode + " 입니다.")

            elif MsgHeader == 'inqTime':    #예약 날짜,시간,주차공간 번호
                self.isRcvTime = True
                inqDate = serverMsg[1]
                if inqDate != 'None':
                    self.inqMonth, self.inqDay = inqDate.split('.')[0], inqDate.split('.')[1]
                    inqTime = serverMsg[2]
                    self.inqTime = inqTime.split(',')
                    self.inqTime.pop()
                    self.inqTime.append(str(int(self.inqTime[-1]) + 1))
                    tmpLot = serverMsg[3]
                    tmpLot = str(ord(tmpLot) - 64)
                    self.inqLot = tmpLot
                elif inqDate == 'None':
                    self.inqMonth = None

            elif MsgHeader == 'EarningList':
                self.month_earning = serverMsg[1]
                self.date_earning = serverMsg[2]
                self.isRcvEarning = True

            elif MsgHeader == 'EarningList_month':
                self.month_earning = serverMsg[1]
                self.isRcvEarning = True



    def serverHandler(self):

        while True:

            if self.isSentID == True:
                command = self.hello()

                if command == '1':
                    cmd_1 = self.hello_1()

                    if cmd_1 == '1':

                        self.reqNonResList()
                        self.long_loading()
                        self.printNonResList()

                        continue
                    elif cmd_1 == '2':

                        continue

                ###예약 페이지
                elif command == '2':

                    cmd_2 = self.hello_2()

                    if cmd_2 == '1': #예약 조회하기 (그 날의 예약 조회 )
                        seeingDate = self.seeing_Date()    #'11.25'
                        self.reqResList(seeingDate)
                        self.waitRcvList()
                        self.printResList()
                        continue


                    elif cmd_2 == '2':    #예약 추가하기
                        resDate = self.resDate()    #'11.25'
                        self.reqResList(resDate)
                        self.waitRcvList()
                        self.printResList()
                        resParkLot , resStart , resEnd = self.resTime()
                        isResPos = self.checkRes(resParkLot,int(resStart),int(resEnd))
                        if isResPos:
                            self.sendRes(resDate,resParkLot,resStart,resEnd)
                            self.waitRcvSucSig()
                            continue
                        else:
                            print("이미 예약된 시간대입니다. 다른 시간대를 선택해 주십시오.")
                            continue


                    elif cmd_2 == '3': #예약 삭제하기
                        seeingDate = self.seeing_Date()    #'11.25'
                        self.reqResList(seeingDate)
                        self.waitRcvList()
                        self.printResList()
                        resParkLot , resStart , resEnd = self.delTime()
                        self.long_loading()
                        self.del_Res(resDate,resParkLot,resStart,resEnd)
                        continue

                    elif cmd_2 =='4':

                        continue





                elif command == '3':

                    command_income = self.income()

                    if command_income == '1':
                        seeingMonth = self.seeing_month()
                        self.reqEarningList_month(seeingMonth)
                        self.long_loading()
                        self.printEarningList_month()

                        continue

                    elif command_income == '2':
                        seeingDate = self.seeing_Date()   #seeingDate = month + '.' + day
                        self.reqEarningList(seeingDate)
                        self.long_loading()
                        self.waitRcvEarning()
                        self.printEarningList()

                        continue

                    elif command_income == '3':

                        continue



                elif command =='4':
                    print("시스템을 종료합니다")
                    os._exit(1)




#######비예약 시스템 함수
    def reqNonResList(self):
        MsgHeader = 'reqNonResList'
        adminMsg = MsgHeader
        self.sock.send(bytes(adminMsg,'utf-8'))


    def printNonResList(self):
        print()
        print("--------------------비예약 주차장 상태입니다----------------")
        count = 0
        for i in self.NonResList:
            if count < 4 or (count > 4 and count < 9):
                print("| %s번 [%s] |" %(count+1,i),end='')
                count += 1
            elif count == 4:
                print("| %s번 [%s] |" %(count+1,i))
                count += 1
            elif count == 9 or count == 14:
                print("| %s번[%s] |" %(count+1,i))
                count += 1
            else:
                print("| %s번[%s] |" %(count+1,i) ,end='')
                count += 1
        print()
        print("------------------------------------------------------------")


#######얘약 시스템 함수
    def waitRcvTime(self):
        while not self.isRcvTime:
            wait = True
        self.isRcvTime = False

    def reqResList(self,resDate):
        MsgHeader = 'reqResList'
        adminMsg = MsgHeader + self.sortMark + resDate
        self.sock.send(bytes(adminMsg,'utf-8'))

    def waitRcvList(self):
        while not self.isRcvList:
            wait = True
        self.isRcvList = False

    def sendRes(self,resDate,resParkLot,resStart,resEnd):
        print("예약을 추가하는 중입니다.. 잠시만 기다려 주십시오")
        MsgHeader = 'postRes'
        adminMsg = MsgHeader + self.sortMark + resDate + self.sortMark + resParkLot + self.sortMark + resStart + self.sortMark + resEnd
        self.sock.send(bytes(adminMsg,'utf-8'))

    def waitRcvSucSig(self):
        while not self.isResSuc:
            wait = True
        print("예약이 완료되었습니다.")
        self.isResSuc = False

    def checkRes(self,resParkLot,resStart,resEnd):
        isResPos = True
        if resParkLot == '1':
            for i in range(resStart,resEnd):
                adminResTime = ' ' + str(i) + ' '
                if adminResTime not in self.parkLot1:
                    isResPos = False
                    break
        elif resParkLot == '2':
            for i in range(resStart,resEnd):
                adminResTime = ' ' + str(i) + ' '
                if adminResTime not in self.parkLot2:
                    isResPos = False
                    break
        elif resParkLot == '3':
            for i in range(resStart,resEnd):
                adminResTime = ' ' + str(i) + ' '
                if adminResTime not in self.parkLot3:
                    isResPos = False
                    break
        elif resParkLot == '4':
            for i in range(resStart,resEnd):
                adminResTime = ' ' + str(i) + ' '
                if adminResTime not in self.parkLot4:
                    isResPos = False
                    break

        return isResPos

    def printResList(self):
        print()
        print("--------------------예약된 시간입니다------------------")
        print("1번공간 " + self.parkLot1)
        print("2번공간 " + self.parkLot2)
        print("3번공간 " + self.parkLot3)
        print("4번공간 " + self.parkLot4)
        print("-----------------------------------------------------")

####예약 조회기능
    def seeing_Date(self): #예약 조회할 때 쓰는 날짜
        print()
        print("--------------------조회시간입력------------------")
        month = input("조회할 월을 입력해주세요 예)12 : ")
        day = input("조회할 일을 입력해주세요 예)25 : ")
        seeingDate = month + '.' + day
        return seeingDate



    def resDate(self):
        print()
        print("--------------------예약시간입력------------------")
        month = input("예약할 월을 입력해주세요 예)12 : ")
        day = input("예약할 일을 입력해주세요 예)25 : ")
        resDate = month + '.' + day
        return resDate

    def resTime(self):
        Lot = input("예약할 주차 공간을 입력하세요 예)2 : ")
        start = input("예약 시작 시간을 입력하세요 예)17 : ")
        end = input("예약 종료 시간을 입력하세요 예)19 : ")
        print("-----------------------------------------------------")
        return (Lot,start,end)

###예약 삭제기능
    def del_Res(self,resDate,resParkLot,resStart,resEnd):
        print("예약을 삭제하는 중입니다.. 잠시만 기다려 주십시오")
        MsgHeader = 'delRes'
        adminMsg = MsgHeader + self.sortMark + resDate + self.sortMark + resParkLot + self.sortMark + resStart + self.sortMark + resEnd
        self.sock.send(bytes(adminMsg,'utf-8'))
        print("예약을 삭제하였습니다.")


    def delTime(self):
        Lot = input("삭제할 주차 공간을 입력하세요 예)2 : ")
        start = input("삭제 시작 시간을 입력하세요 예)17 : ")
        end = input("삭제 종료 시간을 입력하세요 예)19 : ")
        print("-----------------------------------------------------")
        return (Lot,start,end)



################매출관리 기능

    ##월 매출 조회 기능

    def seeing_month(self):
        print()
        print("--------------------조회시간입력------------------")
        month = input("조회할 월을 입력해주세요 예)12 : ")
        seeingMonth = month

        return seeingMonth

    ##일 매출 조회 기능
    def reqEarningList(self,resDate):
        MsgHeader = 'reqEarningList'
        adminMsg = MsgHeader + self.sortMark + resDate
        self.sock.send(bytes(adminMsg,'utf-8'))

    def reqEarningList_month(self,seeingMonth):
        MsgHeader = 'reqEarningList_month'
        adminMsg = MsgHeader + self.sortMark + seeingMonth
        self.sock.send(bytes(adminMsg,'utf-8'))



    def printEarningList(self):

    ##    print("한 달 간 매출은", self.month_earning , "입니다.")
        print("하루 매출은 ", self.date_earning , "입니다.")

    def printEarningList_month(self):

        print("한 달 간 매출은", self.month_earning , "입니다.")




    def waitRcvEarning(self):
        while not self.isRcvEarning:
            wait = True
        self.isRcvEarning = False

    def loading(self):
        time.sleep(0.08)

    def long_loading(self):
        time.sleep(0.5)
        print("로딩중입니다")
#아이디 인증
    def sendID(self):
        ID = 'Admin'
        self.sock.send(bytes(ID,'utf-8'))
        self.isSentID = True



#화면 구현
    def hello(self):
        print()
        print("플랩 주차장 관리자페이지입니다.")
        command = input("1.비예약주차장--------2.예약주차장--------3.매출관리--------4.종료   :")
        return command

    def hello_1(arg):
        print()
        print("비예약관리페이지입니다.")
        cmd_1 = input("1.현재상태조회하기----2.돌아가기 :")
        return cmd_1

    def hello_2(self):
        print()
        print("예약관리페이지입니다.")
        cmd_2 = input("1.예약조회하기----2.예약추가하기----3.예약삭제하기----4.돌아가기 :")
        return cmd_2


    def income(self):
        print()
        print("매출관리 관리자페이지입니다.")
        command_income = input("1.월별 매출관리--------2.일별 매출관리--------3.돌아가기   :")
        return command_income

#실행
C = Admin()
C.run()

