# -*- coding: utf-8 -*-
import pymysql.cursors, time, json, requests, dateutil.parser

#####Параметры MySQL######
HOST = "HOST"            #
USER = "USER"            #
PASSWORD = "PASSWORD"    #
DB = "DB"                #
##########################

#Функция отправки сообщений по SMS
def SmsSend(sms_string, sms_number, url_string):
	sms = requests.get(url_string+"/sms/send?number="+sms_number+"&text="+sms_string+"&sign=SMS Aero&channel=DIRECT").json()
	if sms["success"]==True:
			return True
	return False

#Функция для взаимодействия с одним элементом БД
def MySQLFetchOne(SQLString):
	
	connection = pymysql.connect(host=HOST,user=USER,password=PASSWORD,db=DB,cursorclass=pymysql.cursors.DictCursor)

	try:

	    with connection.cursor() as cursor:
	        cursor.execute(SQLString)
	        result = cursor.fetchone()
	finally:
	    connection.close()
	return result;

#Функция для записи в БД (на самом деле дубляж)
def MySQLWriter(SQLString):
	connection = pymysql.connect(host=HOST,user=USER,password=PASSWORD,db=DB,cursorclass=pymysql.cursors.DictCursor)

	try:
	    with connection.cursor() as cursor:
	        cursor.execute(SQLString)
	    connection.commit()

	finally:
	    connection.close()

def main():

	SMSLogin = MySQLFetchOne("SELECT Val FROM AuthTable WHERE Auth='SMSAeroLogin'")["Val"]
	SMSAPIKey = MySQLFetchOne("SELECT Val FROM AuthTable WHERE Auth='SMSAeroAPIKey'")["Val"]
	SMSNumber = MySQLFetchOne("SELECT Val FROM AuthTable WHERE Auth='SMSNumber'")["Val"]
	SMSAuth = SMSLogin+":"+SMSAPIKey
	all_url = "https://"+SMSAuth+"@gate.smsaero.ru/v2"
	
	while True:
		MyMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/AESIR").json()["royalty"][0]
			
		DateString = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='date'")["Value"]
		Balance = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='balance'")["Value"]
		dateformat = str(dateutil.parser.parse(MyMasternode["paidAt"], dayfirst=True).replace(tzinfo=None)).replace("-","/")

		if (MyMasternode["paidAt"] != None) and (DateString != dateformat):

			ThisPayment = MyMasternode["amount"]
			NewBalance = str(float(Balance)+float(ThisPayment))
			MySQLWriter("UPDATE UniversalTable SET Value='"+dateformat+"' WHERE Service='date'")
			MySQLWriter("UPDATE UniversalTable SET Value='"+NewBalance+"' WHERE Service='balance'")
			GBXPrice = requests.get("https://api.coinmarketcap.com/v2/ticker/2200/?convert=RUB").json()["data"]["quotes"]["RUB"]["price"]
			OutString = str(dateformat)+"\nПополнение: +"+str(ThisPayment)+"GBX ("+str(round(ThisPayment*GBXPrice,2))+" RUB)\nТекущий баланс: "+NewBalance+"GBX ("+str(round(float(NewBalance)*GBXPrice,2))+" RUB)"
			
			if SmsSend(OutString,SMSNumber,all_url) == True:
				print("Успешное информирование о пополнениии за "+dateformat)
			else:
				print("Что-то пошло не так с информированием о пополнениии за "+dateformat)
					
		time.sleep(600)

if __name__ == "__main__":
	main()