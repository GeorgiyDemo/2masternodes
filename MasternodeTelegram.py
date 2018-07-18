# -*- coding: utf-8 -*-
import telegram, pymysql.cursors, time, json, requests, dateutil.parser

#####Параметры MySQL######
HOST = "HOST"            #
USER = "USER"            #
PASSWORD = "PASSWORD"    #
DB = "DB"                #
##########################

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

#Функция отправки сообщений по Телеграму
def TelegramSend(out_string):
	
	bot = telegram.Bot(token=MySQLFetchOne("SELECT Val FROM AuthTable WHERE Auth='TelegramToken'")["Val"])
	bot.send_message(chat_id=-287469302, text=out_string)

def main():
	
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
			TelegramSend(OutString)

		time.sleep(600)

if __name__ == "__main__":
	main()