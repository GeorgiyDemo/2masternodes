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

#Функция получения текущего курса монеты GBX
def GetGBXPrice():
	return requests.get("https://api.coinmarketcap.com/v2/ticker/2200/?convert=RUB").json()["data"]["quotes"]["RUB"]["price"]

def main():
	
	wallets_list = [
		"wallet1",
		"wallet2"
	]

	masternodes_name = {
		0 : "SIF masternode (средняя)\n",
		1 : "SIF masternode (малая)\n",
	}

	masternodes_SQL_names = {
		0 : "Mdate",
		1 : "Sdate",
	}

	while True:

		LargeMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/[MASTERNODE]").json()["royalty"][0]
		if (LargeMasternode["to"] == None):
			LargeMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/[MASTERNODE]").json()["royalty"][1]
		LDateString = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='Ldate'")["Value"]
		LBalance = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='balance'")["Value"]
		dateformat = str(dateutil.parser.parse(LargeMasternode["paidAt"], dayfirst=True).replace(tzinfo=None)).replace("-","/")

		if (LargeMasternode["paidAt"] != None) and (LDateString != dateformat) and (LargeMasternode["to"] != None):

			ThisPayment = LargeMasternode["amount"]
			NewBalance = str(float(LBalance)+float(ThisPayment))
			MySQLWriter("UPDATE UniversalTable SET Value='"+dateformat+"' WHERE Service='Ldate'")
			MySQLWriter("UPDATE UniversalTable SET Value='"+NewBalance+"' WHERE Service='balance'")
			OutString = "HARBARD masternode (большая)\n"+str(dateformat)+"\nПополнение: +"+str(ThisPayment)+"GBX ("+str(round(ThisPayment*GetGBXPrice(),2))+" RUB)\nТекущий баланс: "+NewBalance+"GBX ("+str(round(float(NewBalance)*GetGBXPrice(),2))+" RUB)"
			TelegramSend(OutString)

		for wallet_index in (range(len(wallets_list))):
			
			OtherMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/[MASTERNODE]").json()
			OtherDateString = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='"+masternodes_SQL_names[wallet_index]+"'")["Value"]
			OtherBalance = MySQLFetchOne("SELECT Value FROM UniversalTable WHERE Service='balance'")["Value"]
			main_index = 0

			for royalty in range(len(OtherMasternode["royalty"])):
				
				if (OtherMasternode["royalty"][royalty]["to"]=="gbx/sif/"+wallets_list[wallet_index]):
					dateformat = str(dateutil.parser.parse(OtherMasternode["royalty"][royalty]["paidAt"], dayfirst=True).replace(tzinfo=None)).replace("-","/")
					main_index = royalty
					break

			if (OtherMasternode["royalty"][main_index]["to"]=="gbx/sif/"+wallets_list[wallet_index]) and (OtherDateString != dateformat):

				ThisPayment = OtherMasternode["royalty"][main_index]["amount"]
				NewBalance = str(float(OtherBalance)+float(ThisPayment))
				MySQLWriter("UPDATE UniversalTable SET Value='"+dateformat+"' WHERE Service='"+masternodes_SQL_names[wallet_index]+"'")
				MySQLWriter("UPDATE UniversalTable SET Value='"+NewBalance+"' WHERE Service='balance'")
				OutString = masternodes_name[wallet_index]+str(dateformat)+"\nПополнение: +"+str(ThisPayment)+"GBX ("+str(round(ThisPayment*GetGBXPrice(),2))+" RUB)\nТекущий баланс: "+NewBalance+"GBX ("+str(round(float(NewBalance)*GetGBXPrice(),2))+" RUB)"
				TelegramSend(OutString)

		time.sleep(300)

if __name__ == "__main__":
	main()