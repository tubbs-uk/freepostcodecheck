from lxml import html
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import sys
import re

# uses 3rd party libraries: lxml, requests, PIL, pytesseract

if len(sys.argv) != 3:
    print "usage: " + sys.argv[0] + " <postcode> <email>"
    sys.exit(1)

def checkOk(response, errMsg):
    if response.status_code != 200:
        print "error: " + errMsg + ". status = " + str(response.status_code) + " reason = " + response.reason
        sys.exit(1)

def postcodeOk(postcode):
    if ' ' not in postcode:
        return (False, "no space")
    if len(postcode) < 5 or len(postcode) > 8:
        return (False, "wrong length")

    outcode, incode = postcode.split(' ')
    if len(outcode) < 2 or len(outcode) > 4:
        return (False, "wrong length of outward code")
    if len(incode) != 3:
        return (False, "wrong length of outward code")

    if not re.match(r'^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$', postcode.upper()):
        return (False, "postcode not valid")
    if not re.match(r'[a-zA-Z]{1,2}\d{1,2}', outcode) and not re.match(r'\d{1,2}[a-zA-Z]\d', outcode):
        return (False, "outward code not valid")
    if not re.match(r'\d[a-zA-Z][a-zA-Z]', incode):
        return (False, "inward code not valid")

    return True

mypostcode = sys.argv[1]
myemail = sys.argv[2]

session = requests.Session()
homePageResponse = session.get('http://freepostcodelottery.com')
checkOk(homePageResponse, "failed to request homepage")

# TODO sleep random number of seconds

loggedinpage = session.post('http://freepostcodelottery.com', data = {'register-ticket':mypostcode, 'register-email': myemail, 'login':''})
checkOk(loggedinpage, "failed to login")
tree = html.fromstring(loggedinpage.content)

postcodeImg = tree.xpath('//*[@id="main-results-container"]/div/div[2]/div[1]/img')
if len(postcodeImg) == 0:
    print "no winning postcode image found"
else:
    imgSrc = postcodeImg[0].attrib.get('src')

    imgData = session.get('http://freepostcodelottery.com' + imgSrc)
    checkOk(imgData, "failed to get main winning postcode image")
    winningPostcodeImg = Image.open(BytesIO(imgData.content))

    winningPostcodeString = pytesseract.image_to_string(winningPostcodeImg)
    print 'main draw postcode =', winningPostcodeString

    print postcodeOk('st11 9tg')

bonusPostcode = tree.xpath('//*[@id="mini-draw"]/p[2]')
if len(bonusPostcode) == 0:
    print "no bonus postcode found"
else:
    print 'bonus postcode =', bonusPostcode[0].text
