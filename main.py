import tweepy

import time 
import pprint
import secrets
import config
from binance.client import Client

MyTwitterId = '499189739'
ElonMustTwitterId = '44196397'
expendableUSDT = 10             #USDT willing to spend to dogecoin
startPrice = 0
curPrice = 0                    #current price 
highestPrice = 0        #keep track if highest price after tweet triggering buy order
quantityOfDogesToBuy = 50                #ammount of doges baught

#Todo link to binance API and we should have a working beta already 
#now lets hide these keys to i can push my code to github
#Todo once i have a fix ip get allow access with the key ONLY FROM THAT IP ADDRESS ( for extra security)


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
            return prices[i]['price']
    return 0


#TODO TEST launchPriceTracker
#Beggins tracking price of DOGE and sells if price drops by more then 20% of highest price
def launchPriceTracker(): 
    print("enterPriceTracker")
    print("start price : {}".format(startPrice))
    #begin updating price put in a timer to calls this functions every like 10 secs     
    curPrice = getCurPrice()
    if(curPrice == 0): exit()
    if(highestPrice < curPrice - 0.02):
        highestPrice = curPrice
    
    priceDiffToCur = curPrice - startPrice
    priceDiffToHighest = highestPrice - startPrice

    if(priceDiffToCur < 0  | priceDiffToHighest < 0 ): 
         order = client.order_market_sell(symbol='DOGEUSDT', quantity = expendableUSDT)

    if((curPrice - startPrice)/(highestPrice - startPrice) < 8./10.) : 
        order = client.order_market_sell(symbol='DOGEUSDT', quantity = expendableUSDT) #todo thing about cashing out same amount of doges i baught
        #if order fails what to do ? try again with lower amount of expendableUSDT? 
        print("sold doges: {}".format(order))
        exit() #once we sold we can exit 
    
    time.sleep(5.) #sleep for 5 seconds before tracking again
    launchPriceTracker()

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if from_creator(status):
            tweet = status.text.lower()
            if "doge" in tweet:
                startPrice = getCurPrice()
                highestPrice = startPrice
                #order = client.order_market_buy(symbol='DOGEUSDT', quantity = quantityOfDogesToBuy) #TODO smarter way of defining nDogeCoins upper bounded by my quantitiy dogecoins 
                #print(order) 
                #here add some variables to record some info on the order
                print("executed order")
                launchPriceTracker()
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
startPrice = getCurPrice()
highestPrice = startPrice
launchPriceTracker()
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