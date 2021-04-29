import tweepy

import time 
import pprint
import secrets
import config
from binance.client import Client


#Note: in python these are NOT global variables you have to writte globan in front of them for them to be global
MyTwitterId = '499189739'                #my own personal twitter id 
ElonMustTwitterId = '44196397'           #ElonMusk twitter id 
expendableUSDT = 10                      #USDT willing to spend to dogecoin
quantityOfDogesToBuy = 50                #ammount of doges baught

#TODO once i have a fix ip get allow access with the key ONLY FROM THAT IP ADDRESS ( for extra security)

#Connect to twitter API 
auth = tweepy.OAuthHandler(config.twAPIKey, config.twAPISKEY)
auth.set_access_token(config.twAPIToken, config.twAPISToken)
api = tweepy.API(auth)

#Connect to Binance API 
client = Client(config.BkEY, config.bSKey)
print("connected to API's")

#Filters out mentions and RTs
def from_creator(status): #might want to change the filter here, if elon retweens a doge meme i want to get that!!
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    else:
        return True

#Gets current price of DOGE IN USDT 
def getCurPrice(): 
    prices = client.get_all_tickers()
    for i in range(len(prices)):
        if(prices[i]['symbol'] == 'DOGEUSDT') : 
            return float(prices[i]['price'])
    return 0


#TODO TEST launchPriceTracker
#Beggins tracking price of DOGE and sells if price drops by more then 20% of highest price
def launchPriceTracker(curHighestPrice, startPrice): 
    #begin updating price put in a timer to calls this functions every like 10 secs    
    highestPrice = curHighestPrice
    curPrice = getCurPrice()
    if(curPrice == 0): exit() #error
    if(highestPrice < curPrice):
        highestPrice = curPrice #update highest price since start
    

    print("startPrice: " + str(startPrice))
    print("curPrice :" + str(curPrice))
    print("highestPrice: " + str(highestPrice))

    priceDiffToCur = (curPrice - startPrice) 
    priceDiffToHighest = (highestPrice - startPrice) 

    #if we are losing money then sell
    if(priceDiffToCur < -0.2  or priceDiffToHighest < -0.2 ): 
         #order = client.order_market_sell(symbol='DOGEUSDT', quantity = expendableUSDT)
         print("tries to sell doges first if ")
         exit()

    #TODO mmh defo need to be carefull here cuz the diff is sometimes NEGATIVE!! so should take absolute value!! but then how do i take into  account the fact the vlaue is negative 
    if(priceDiffToHighest != 0 and (priceDiffToCur)/(priceDiffToHighest) < 6.5/10.) : #if fall by 35% below local highest then sell 
        print("tries to sell doges the div is: " +  str(priceDiffToCur) +" "+ str(priceDiffToHighest) + " "+ str((priceDiffToCur)/(priceDiffToHighest)))
        #order = client.order_market_sell(symbol='DOGEUSDT', quantity = expendableUSDT) #todo thing about cashing out same amount of doges i baught
        #if order fails what to do ? try again with lower amount of expendableUSDT? 
        #print("sold doges: {}".format(order))
        exit() #once we sold we can exit 
    
    time.sleep(5.) #sleep for 5 seconds before tracking again
    launchPriceTracker(highestPrice, startPrice)

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if from_creator(status):
            tweet = status.text.lower()
            if "doge" in tweet:
                order = client.order_market_buy(symbol='DOGEUSDT', quantity = quantityOfDogesToBuy) #TODO smarter way of defining nDogeCoins upper bounded by my quantitiy dogecoins 
                print(order) 
                #here add some variables to record some info on the order
                print("executed order")
                startPrice = getCurPrice()
                launchPriceTracker(startPrice, startPrice)
            return True
        return True


    def on_error(self, status_code):
        if status_code == 420:
            print("Error 420")
            #returning False in on_error disconnects the stream
            return False
    
#create stream and keep twitter accounts i choose to follow
#myStreamListener = MyStreamListener()
#myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)       
#myStream.filter(follow=[MyTwitterId, ElonMustTwitterId])
#add tesla account, spacex and also companies, mavericks, mark cuban, companies who might it, also coinbase!!! ect.. (try to asses if the tweets are good can also be an improvement)
launchPriceTracker(getCurPrice(), getCurPrice())
print("listening...")







#possible optimisations : check more the one user, get more words, organise code better maybe even use 1 folder for classes, HIDE CREDS ect.. 


#=============EXAMPLES OF HOW TO WORK WITH BINANCE API =======================================================================================================
#info = client.get_symbol_info('BNBBTC')
#for i in info:
#   print(i)

#info = client.get_account()
#print(info)
#bal = info['balances']
#for b in bal: 
#    if float(b['free']) > 0:
#        print(b)

#gets last trades with this pair (BNBBTC) buy = BUY BNB (SELL BTC) (i think)
#trades = client.get_my_trades(symbol = 'BNBBTC')

#GIVEN THE DIFFERENT STRUCTURE OF THE JSON here its a list of jsons, we need to access the jsons with indices and then can use the field (for balance it was a json with other jsons inside)
#prices = client.get_all_tickers()
#print(prices)
#for i in range(len(prices)):
#    if(prices[i]['symbol'] == 'DOGEUSDT') : 
#        print(prices[i]['price'])

#The tutorial i used, hes got alot of other vids on blockahin or how
#to create my own crypto 
# https://www.youtube.com/watch?v=3uxAn7EBSS0&t=196s
#to make an order its easy just check documentation on binance  https://python-binance.readthedocs.io/en/latest/binance.html