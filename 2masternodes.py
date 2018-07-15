import requests, threading, dateutil.parser
MyMasternode = requests.get("https://api.2masternodes.com/api/coin/gbx/masternode/[MASTERNODE_NAME]").json()
wallets_list = ["[WALLET1]","[WALLET2]"]

def main():
	try:
		OutString = ""
		PaymentsStr = ""
		for wallet in wallets_list:
			for i in range(len(MyMasternode["beneficiaries"])):
				if (wallet == MyMasternode["beneficiaries"][i]["address"]):
					BufWallet = MyMasternode["beneficiaries"][i]
					OutString += "Адрес: "+BufWallet["address"]+", "+str(BufWallet["share"])+"%, кол-во "+str(BufWallet["amount"])+"\n"

			counter = 0
			for royalty in range(len(MyMasternode["royalty"])):
				if (counter == 1):
					break
				if (MyMasternode["royalty"][royalty]["to"]=="gbx/sif/"+wallet):
					counter += 1
					BufPayment = MyMasternode["royalty"][royalty]
					dateformat = dateutil.parser.parse(BufPayment["paidAt"], dayfirst=True).replace(tzinfo=None)
					PaymentsStr += "   ["+str(dateformat)+"] "+str(BufPayment["amount"])+" -> "+wallet+"\n"

		print(OutString)
		print(PaymentsStr)
	except:
		print("Нет подключения к сети")

if __name__ == "__main__":
	main()



