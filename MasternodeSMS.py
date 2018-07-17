# -*- coding: utf-8 -*-
from pytils import numeral
import pymysql.cursors
import string, vk, time, datetime, json, requests, urllib3, dateutil.parser

#####Параметры MySQL######
HOST = "HOST"            #
USER = "USER"            #
PASSWORD = "PASSWORD"    #
DB = "DB"                #
##########################

def SmsSend(sms_string):
	print(sms_string)

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
	while True:
		MyMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/[MASTERNODE_NAME]").json()["royalty"][0]
		print(MyMasternode)

			
		DateString = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='date'")["Value"]
		Balance = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='balance'")["Value"]
		dateformat = str(dateutil.parser.parse(MyMasternode["paidAt"], dayfirst=True).replace(tzinfo=None)).replace("-","/")
				
		print(DateString)
		print(dateformat)

		if (MyMasternode["paidAt"] != None) and (DateString != dateformat):

			ThisPayment = MyMasternode["amount"]
			NewBalance = str(float(Balance)+float(ThisPayment))
			MySQLWriter("UPDATE UniversalTable SET Value='"+dateformat+"' WHERE Service='date'")
			MySQLWriter("UPDATE UniversalTable SET Value='"+NewBalance+"' WHERE Service='balance'")
					
			print(str(dateformat)+"\nПополнение: +"+str(ThisPayment)+"GBX\nТекущий баланс: "+NewBalance+"GBX")
			print("Успешное информирование о пополнениии за "+dateformat)
					#print("Что-то пошло не так")
					
		time.sleep(10)

if __name__ == "__main__":
	main()