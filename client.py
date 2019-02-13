import socket
import threading
import sys
import os
import time

class Client:
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


    def __init__(self,address):
        self.sock.connect((address,4969))

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




    def serverHandler(self):
        while True:
            if self.isSentID == True:
                cmd = self.setCmdWindow()

                if cmd == '1':
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
                elif cmd == '2':
                    clientACode = self.clientACode()
                    self.inqRes(clientACode)
                    self.waitRcvTime()
                    self.printInqRes()
                    continue
                elif cmd == '3':
                    print("예약 프로그램을 종료합니다.")
                    os._exit(1)

    def printInqRes(self):
        print()
        print("----------------------예약조회결과--------------------")
        if self.inqMonth == None:
            print("예약시 발급받은 인증코드가 아닙니다.")
            print("-----------------------------------------------------")
        else:
            print("고객님은 " + self.inqMonth + "월 " + self.inqDay + "일, "
            "주차공간 " + self.inqLot + "번에 " + self.inqTime[0] + "시부터 "
            + self.inqTime[-1] + "시까지 예약하셨습니다.")
            print("-----------------------------------------------------")


    def clientACode(self):
        print()
        print("----------------------인증코드입력--------------------")
        ACode = input("예약시 발급받은 인증코드를 입력하세요 : ")
        print("-----------------------------------------------------")
        return ACode

    def inqRes(self,clientACode):
        MsgHeader = 'inqResTime'
        clientMsg = MsgHeader + self.sortMark + clientACode
        self.sock.send(bytes(clientMsg,'utf-8'))

    def waitRcvTime(self):
        while not self.isRcvTime:
            wait = True
        self.isRcvTime = False

    def reqResList(self,resDate):
        MsgHeader = 'reqResList'
        clientMsg = MsgHeader + self.sortMark + resDate
        self.sock.send(bytes(clientMsg,'utf-8'))

    def waitRcvList(self):
        while not self.isRcvList:
            wait = True
        self.isRcvList = False

    def sendRes(self,resDate,resParkLot,resStart,resEnd):
        print("예약중입니다.. 잠시만 기다려 주십시오")
        MsgHeader = 'postRes'
        clientMsg = MsgHeader + self.sortMark + resDate + self.sortMark + resParkLot + self.sortMark + resStart + self.sortMark + resEnd
        self.sock.send(bytes(clientMsg,'utf-8'))

    def waitRcvSucSig(self):
        while not self.isResSuc:
            wait = True
        print("예약이 완료되었습니다.")
        self.isResSuc = False

    def checkRes(self,resParkLot,resStart,resEnd):
        isResPos = True
        if resParkLot == '1':
            for i in range(resStart,resEnd):
                clientResTime = str(i) + ' '
                if clientResTime not in self.parkLot1:
                    isResPos = False
                    break
        elif resParkLot == '2':
            for i in range(resStart,resEnd):
                clientResTime = str(i) + ' '
                if clientResTime not in self.parkLot2:
                    isResPos = False
                    break
        elif resParkLot == '3':
            for i in range(resStart,resEnd):
                clientResTime = str(i) + ' '
                if clientResTime not in self.parkLot3:
                    isResPos = False
                    break
        elif resParkLot == '4':
            for i in range(resStart,resEnd):
                clientResTime = str(i) + ' '
                if clientResTime not in self.parkLot4:
                    isResPos = False
                    break

        return isResPos

    def printResList(self):
        print()
        print("--------------------예약가능시간------------------")
        print("1번공간 " + self.parkLot1)
        print("2번공간 " + self.parkLot2)
        print("3번공간 " + self.parkLot3)
        print("4번공간 " + self.parkLot4)
        print("-----------------------------------------------------")


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

    def sendID(self):
        ID = 'Client'
        self.sock.send(bytes(ID,'utf-8'))
        self.isSentID = True

    def setCmdWindow(self):
        print()
        print("플랩 주차장 예약 페이지에 오신 것을 환영합니다.")
        cmd = input("1.예약하기------------2.예약조회-----------3.종료    :")
        return cmd

C = Client(sys.argv[1])
C.run()
