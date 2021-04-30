import tweepy
import time 
import pprint
import secrets
import sys
import config
import math
from binance.client import Client


#Note: how global vars work
#TODO improvements !! use limit sells!! they are safer! as market sells dont work if the price is dumping HARD or mooning HARD! 
#in those extreme cases you are forced to limit buy/sell 

MyTwitterId = '499189739'                #my own personal twitter id 
ElonMustTwitterId = '44196397'           #ElonMusk twitter id 
expendableUSDT = 300                     #USDT willing to allow the bot to spend to dogecoin
baughtDoges = 0.                         #ammount of doges baught

#TODO once i have a fix ip get allow access with the key ONLY FROM THAT IP ADDRESS ( for extra security)

#Connect to twitter API 
auth = tweepy.OAuthHandler(config.twAPIKey, config.twAPISKEY)
auth.set_access_token(config.twAPIToken, config.twAPISToken)
api = tweepy.API(auth)

#Connect to Binance API 
client = Client(config.BkEY, config.bSKey)
print("connected to API's")

#Filters out mentions and RTs, only keeps tweets made by the creator
def from_creator(status): 
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

#return how many doges i can buy with my usdt (we use a 0.1 safety margin) and truncate to and int for simplicity
def usdtToDoges(usdt) :
    return int(usdt/(getCurPrice() + 0.1))

#Beggins tracking price of DOGE and sells if price drops by more then 35% of highest price 
def launchPriceTracker(curHighestPrice, startPrice): 
    time.sleep(120.) #check every 2 minutes
   
    highestPrice = curHighestPrice
    curPrice = getCurPrice()
    if(curPrice == 0): exit() #error
    if(highestPrice < curPrice):
        highestPrice = curPrice #update highest price since buy order
    
    priceDiffToCur = (curPrice - startPrice) 
    priceDiffToHighest = (highestPrice - startPrice) 

    #if current price or highest price if lower then starting price (this means price went down instead of up) then sell
    if(priceDiffToCur < -0.2  or priceDiffToHighest < -0.2 ): 
         order = client.order_market_sell(symbol='DOGEUSDT', quantity = baughtDoges)
         sys.stdout.flush()
         print(order)
         exit()

    
    if(priceDiffToHighest != 0 and math.fabs((priceDiffToCur)/(priceDiffToHighest)) < 6.5/10.) : #if fall by 35% below local highest then sell 
        print("tries to sell doges the div is: " +  str(priceDiffToCur) +" "+ str(priceDiffToHighest) + " "+ str((priceDiffToCur)/(priceDiffToHighest)))
        order = client.order_market_sell(symbol='DOGEUSDT', quantity = baughtDoges) #todo thing about cashing out same amount of doges i baught
        print(order)
        exit()

    launchPriceTracker(highestPrice, startPrice)

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if from_creator(status): 
            tweet = status.text.lower()
            if "doge" or "hodl" or "coin" or "dog" or "hold" or "bark" or "shiba" \
                or "inu" in tweet:
                quantityOfDogesToBuy = usdtToDoges(expendableUSDT)
                order = client.order_market_buy(symbol='DOGEUSDT', quantity = quantityOfDogesToBuy) #TODO smarter way of defining nDogeCoins upper bounded by my quantitiy dogecoins 
                print(order) 
                global baughtDoges 
                baughtDoges = quantityOfDogesToBuy #record the number of doges baught
                print("order status: " + order['status'])
                sys.stdout.flush()
                startPrice = getCurPrice()
                if(order['status'] == 'FILLED'):
                    launchPriceTracker(startPrice, startPrice)
                else:
                    exit() #error
            return True
        return True


    def on_error(self, status_code):
        if status_code == 420:
            print("Error 420")
            #returning False in on_error disconnects the stream
            return False
    
#create stream and keep twitter accounts i choose to follow
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)       
myStream.filter(follow=[MyTwitterId, ElonMustTwitterId])
#add tesla account, spacex and also companies, mavericks, mark cuban, companies who might it, also add coinbase!!! ect.. (try to asses if the tweets are good can also be an improvement)

print("listening...")







#possible optimisations : check more the one user, get more words, organise code better maybe even use 1 folder for classes, HIDE CREDS ect.. 

#Debugging prints
#print("startPrice: " + str(startPrice))
#print("curPrice :" + str(curPrice))
#print("highestPrice: " + str(highestPrice))

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