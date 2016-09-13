from lxml import html, etree
import requests
import sys
import freeutil
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

# uses 3rd party libraries: lxml, requests, PIL, pytesseract, cssselect

# main draw resets once a day at 12 noon
# bonus draw resets and appears once a day at 6pm till 12 midnight
# stackpot draws refresh every 12 hours at 9am and 9pm

# todo:
# only email on match, error, or invalid postcode
# split into separate invocations for draw types and times
# sms on match
# run in cloud
# sign up with real email - DONE
# run at at slightly diff times

if len(sys.argv) != 7:
    print "usage: " + sys.argv[0] + " <postcode> <email> <twilio account sid> <twilio auth token> <twilio from number> <my mobile number>"
    sys.exit(1)

mypostcode = sys.argv[1]
myemail = sys.argv[2]
twilioSid = sys.argv[3]
twilioToken = sys.argv[4]
twilioFromNumber = sys.argv[5]
myMobile = sys.argv[6]

smsclient = TwilioRestClient(twilioSid, twilioToken)

session = requests.Session()
homePageResponse = session.get('http://freepostcodelottery.com')
freeutil.checkOk(homePageResponse, "failed to request homepage")

freeutil.randsleep()

# main and bonus postcode draws
loggedinpage = session.post('http://freepostcodelottery.com', data = {'register-ticket':mypostcode, 'register-email': myemail, 'login':''})
freeutil.checkOk(loggedinpage, "failed to login")
maintree = html.fromstring(loggedinpage.content)

postcodeImg = maintree.xpath('//*[@id="main-results-container"]/div/div[2]/div[1]/img')
mainCodeOk, mainCode = freeutil.checkPostcodeImage('main', session, postcodeImg)

bonusPostcode = maintree.xpath('//*[@id="mini-draw"]/p[2]')
bonusOk, bonusCode = freeutil.checkPostcodeString("bonus", bonusPostcode)

# stackpot
stackpage = session.get('http://freepostcodelottery.com/stackpot')
freeutil.checkOk(stackpage, "failed to get stackpot page")
stacktree = html.fromstring(stackpage.content)

stackBoard = stacktree.cssselect('#middle > div.results-board')
stackResults = []
if not len(stackBoard):
    print "no stackpot results board found"
else:
    si=1
    for res in stackBoard[0].findall('.//span'):
        stackResults.append(freeutil.checkPostcodeString("stackpot"+str(si), [res]))
    si += 1

smsMessage = ""
if mainCodeOk:
    if freeutil.checkPostcodeMatch(mypostcode, mainCode):
        smsMessage += "Match on maincode! " + mainCode
else:
    smsMessage += "invalid maincode " + mainCode

if bonusOk:
    if freeutil.checkPostcodeMatch(mypostcode, bonusCode):
        smsMessage += " Match on bonuscode! " + bonusCode
else:
    smsMessage += " invalid bonuscode " + bonusCode

sri = 1
for sr in stackResults:
    if sr[0]:
        if freeutil.checkPostcodeMatch(mypostcode, sr[1]):
            smsMessage += " Match on stackpot code " + str(sri) + "! " + sr[1]
    else:
        smsMessage += " invalid stackpot code " + str(sri) + sr[1]
    sri += 1

try:
    if smsMessage:
        message = smsclient.messages.create(to=myMobile, from_=twilioFromNumber, body=smsMessage)
except TwilioRestException as e:
    print("Error calling Twilio SMS service: " + str(e))
