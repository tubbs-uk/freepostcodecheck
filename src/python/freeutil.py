import re, sys
import random, time
from PIL import Image
from io import BytesIO
import pytesseract

random.seed()

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
        return (False, "postcode not valid via regex")
    if not re.match(r'[A-Z]{1,2}\d{1,2}', outcode) and not re.match(r'\d{1,2}[A-Z]\d', outcode.upper()):
        return (False, "outward code not valid")
    if not re.match(r'\d[A-Z][A-Z]', incode.upper()):
        return (False, "inward code not valid")

    return (True, "ok")

def randsleep():
    time.sleep(random.randint(2, 5))

def checkPostcodeImage(type, session, imageSrc):
    if len(imageSrc) == 0:
        print "no " + type + " postcode image found"
        return (False, "no postcode image")
    else:
        imgSrc = imageSrc[0].attrib.get('src')

        imgData = session.get('http://freepostcodelottery.com' + imgSrc)
        checkOk(imgData, "failed to get " + type + " postcode image")
        postcodeImg = Image.open(BytesIO(imgData.content))

        postcodeString = pytesseract.image_to_string(postcodeImg)
        print type + " postcode = " + postcodeString

        codeOk, msg = postcodeOk(postcodeString)
        if codeOk:
            print type + " postcode is valid"
        else:
            print type + " postcode not valid: " + msg
        return (codeOk, postcodeString)

def checkPostcodeString(type, textSrc):
    postcodeStr = textSrc[0].text.replace('\n', '').strip()

    if len(textSrc) == 0:
        print "no " + type + " postcode found"
        return (False, "no postcode found")
    else:
        print type + " postcode = " + postcodeStr

        codeOk, msg = postcodeOk(postcodeStr)
        if codeOk:
            print type + " postcode is valid"
        else:
            print type + " postcode not valid: " + msg
        return (codeOk, postcodeStr)

def checkPostcodeMatch(myPostcode, checkPostcode):
    myoutcode, myincode = myPostcode.split(' ')
    choutcode, chincode = checkPostcode.split(' ')

    if myoutcode.upper() == choutcode.upper():
        return True
    return False
