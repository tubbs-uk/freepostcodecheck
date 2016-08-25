from lxml import html
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import sys

# uses 3rd party libraries: lxml, requests, PIL, pytesseract

if len(sys.argv) != 3:
    print "usage: " + sys.argv[0] + " <postcode> <email>"
    sys.exit(1)

mypostcode = sys.argv[1]
myemail = sys.argv[2]

session = requests.Session()
session.get('http://freepostcodelottery.com')

loggedinpage = session.post('http://freepostcodelottery.com', data = {'register-ticket':mypostcode, 'register-email': myemail, 'login':''})
tree = html.fromstring(loggedinpage.content)

postcodeImg = tree.xpath('//*[@id="main-results-container"]/div/div[2]/div[1]/img')
imgSrc = postcodeImg[0].attrib.get('src')

imgData = session.get('http://freepostcodelottery.com' + imgSrc)
winningPostcodeImg = Image.open(BytesIO(imgData.content))

winningPostcodeString = pytesseract.image_to_string(winningPostcodeImg)
print 'main draw postcode =', winningPostcodeString

bonusPostcode = tree.xpath('//*[@id="mini-draw"]/p[2]')
print 'bonus postcode =', bonusPostcode[0].text