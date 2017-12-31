import sys
import os
import json
import logging
import datetime
import yaml
import requests
from hellosign_sdk import HSClient
import time

from django.conf import settings

creds = yaml.load(open('creds.yml'))
FAX_API_ACCOUNT = creds['helaineHelloFaxAPIKey']
FAX_PASSWORD = creds['helaineHelloFaxPassword']
FAX_EMAIL = creds['helaineHelloFaxEmail']
listOfSignRequests = []
_myDictSignatureRequestID_ToEmail = {}


def timeStamped(fmt='%Y-%m-%d-%H-%M-%S'):
    return datetime.datetime.now().strftime((fmt))

date = timeStamped()
LOG_FILE = "faxapi-" + date + ".log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
logging.debug('Logging has started for the FAX API APPLICATION')


DEBUG = os.environ.get('DEBUG', 'on') == 'on'
CSRF_COOKIE_SECURE = False
SECRET_KEY = os.environ.get('SECRET_KEY', '{{ secret_key }}')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/Users/alexmcferron/onlinefaxmachine/onlinefaxmachine/faxit/templates/',],
        'APP_DIRS' : True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

settings.configure(
    DEBUG=DEBUG,
    TEMPLATES=TEMPLATES,
    SECRET_KEY=SECRET_KEY,
    ALLOWED_HOSTS=ALLOWED_HOSTS, 
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
)



from django.views.decorators.csrf import csrf_exempt

from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse




@csrf_exempt
def post(request, *args):
    response = HttpResponse("Hello API Event Received")

    #parseData(request)
    #print(request.body)



    parseHelloSignData(request, "post")


    return response

@csrf_exempt
def postHelloWorks(request, *args):

    print("postHelloWorks")

    response = HttpResponse("Hello API Event Received")
    return response

#This is used for the HelloSign API and should be removed from this app
@csrf_exempt
def appCallback(request, *args):
    response = HttpResponse("Hello API Event Received")

    parseHelloSignData(request, 'post_APP')

    return response

#This is used for the HelloSign API and should be removed from this app
@csrf_exempt
def parseHelloSignData(request, methodHit):
    try:

        data = json.loads(request.POST.get('json'))
        event = data['event']

        event_type = event['event_type']

        if event_type == 'signature_request_sent':
            print("EVENT TYPE is signature_request_sent")
            sigrequest = data['event']['event_metadata']
            print(sigrequest)
            message = utilTimeStampAndMessage("TIME OF SIGNATURE_REQUEST_SENT")
            print(message)
        elif event_type == 'signature_request_viewed':
            print("EVENT TYPE is signature_request_viewed")
            sigrequest = data['event']['event_metadata']
            print(sigrequest)
            message = utilTimeStampAndMessage("TIME OF SIGNATURE_REQUEST_VIEWED")
            print(message)



        print("BEGIN \n")
        print(methodHit + "\n")
        print(event_type + "\n")
        print("\n")
        print(event)

        print("END \n")

    except:
        message = sys.exc_info()[0]
        print("Unexpected error:", sys.exc_info()[0])
        logging.debug("Exception thrown - parseHelloSignData")

@csrf_exempt
def parseData(request):

    try:
        str_response = request.body.decode("utf-8")
        frontChopNumber = str_response.find('{"Transaction"')
        backChopNumber = str_response.find('}}')
        choppedStr_response = str_response[frontChopNumber:backChopNumber + 2]
        jsonResult = json.loads(choppedStr_response)
        print(jsonResult['Transaction']['StatusCode'])

        logging.info("BEGIN Callback information\n")
        logging.info("GUID= " + jsonResult['Transaction']['Guid'])
        logging.info("TO= " + jsonResult['Transaction']['To'])
        logging.info("FROM= " + jsonResult['Transaction']['From'])
        logging.info("IsInbound")
        logging.info(jsonResult['Transaction']['IsInbound'])
        #logging.info("IsDraft")
        #logging.info(jsonResult['Transaction']['IsDraft'])
        #logging.info("TypeCode " + jsonResult['Transaction']['TypeCode'])
        #logging.info("StatusCode " + jsonResult['Transaction']['StatusCode'])
        #logging.info("ErrorCode")
        logging.info(jsonResult['Transaction']['ErrorCode'])
        logging.info("CreatedAt= " + jsonResult['Transaction']['CreatedAt'])
        logging.info("UpdatedAt= " + jsonResult['Transaction']['UpdatedAt'])
        logging.info("Uri= " + jsonResult['Transaction']['Uri'])
        logging.info("NumPagesBilled")
        logging.info(jsonResult['Transaction']['NumPagesBilled'])
        logging.info("END Callback information\n")

    except TypeError:
        print(sys.exc_info()[0])
    except:
        message = sys.exc_info()[0]
        print("Unexpected error:", sys.exc_info()[0])
        logging.debug("Exception thrown - parseData")

from django.template import loader

@csrf_exempt
def index(request):

    template = loader.get_template('index.html')
    return HttpResponse(template.render())

@csrf_exempt
def sign(request):

    template = loader.get_template('sign.html')
    return HttpResponse(template.render())


from django.shortcuts import render


@csrf_exempt
def sendsigrequest(request):

    apikey = creds['alexmcferronAPIKEY']
    clientID = creds['alexmcferronClientID']
    client = HSClient(api_key=apikey)
    #account = client.get_account_info()
    #emailaddress = client.account.email_address


    response = client.send_signature_request_embedded(

        test_mode=True,
        client_id=clientID,
        files=["slowpdf2.pdf"],
        title="embedded",
        subject="Ticket 277902",
        message="Ticket 277902",
        signers=[
            {'email_address': 'alex.mcferron@hellosign.com', 'name': 'andrew'}
            #{'email_address': 'alexmac2019@gmail.com', 'name': 'freedom'}
        ],
        use_text_tags=False,

    )

    exploreSignatureRequestResponseObject(response)
    print(response)

    message = utilTimeStampAndMessage("TIME SIGNATURE REQUEST CREATED - call is finished")
    print(message)

    sigRequestURL = 'notSet'

    if len(listOfSignRequests) > 0:
        mySignatureID = listOfSignRequests.pop(0)
        sigRequestURL = client.get_embedded_object(mySignatureID)
        print(mySignatureID + " =signatureID")
        print(_myDictSignatureRequestID_ToEmail[mySignatureID])

    urlOnly = sigRequestURL.sign_url


    results = {}
    results.update({'TempUrl': urlOnly})
    results.update({'clientID' : clientID})

    message = utilTimeStampAndMessage("CALLING THE IFRAME NOW ALEX M")
    print(message)
    return render(request, "sign.html", results)


@csrf_exempt
def accountinfo(request):
    urlstring = "https://" + FAX_EMAIL + ":" + FAX_PASSWORD + "@api.hellofax.com/v1/Accounts/" + FAX_API_ACCOUNT
    r = requests.get(urlstring)
    jsonResult = json.loads(r.text)
    results = {}
    ShouldSendOutboundConfEmails = jsonResult['Account']['ShouldSendOutboundConfEmails']
    ShouldIncludePdfsInReceivedFaxEmails = jsonResult['Account']['ShouldIncludePdfsInReceivedFaxEmails']
    DefaultOutboundFaxCallbackUrl = jsonResult['Account']['DefaultOutboundFaxCallbackUrl']
    DefaultInboundFaxCallbackUrl = jsonResult['Account']['DefaultInboundFaxCallbackUrl']
    Guid = jsonResult['Account']['Guid']

    #results = {}
    results.update({'ShouldSendOutboundConfEmails': ShouldSendOutboundConfEmails})
    results.update({'ShouldIncludePdfsInReceivedFaxEmails': ShouldIncludePdfsInReceivedFaxEmails})
    results.update({'DefaultOutboundFaxCallbackUrl': DefaultOutboundFaxCallbackUrl})
    results.update({'DefaultInboundFaxCallbackUrl': DefaultInboundFaxCallbackUrl})
    results.update({'Guid': Guid})
    return render(request, "index.html", results)

@csrf_exempt
def setcallbackfunction(request):
    urlstring = "https://" + FAX_EMAIL + ":" + FAX_PASSWORD + "@api.hellofax.com/v1/Accounts/" + FAX_API_ACCOUNT
    allData = request.POST
    newCallbackValue = allData.get("callback_value")
    newCallbackValue = newCallbackValue + "/post"
    print(newCallbackValue)

    print(type(newCallbackValue))
    data = {
        'DefaultInboundFaxCallbackUrl': newCallbackValue,
        'DefaultOutboundFaxCallbackUrl': newCallbackValue
    }
    r = requests.post(urlstring, data)

    return render(request, "index.html")

urlpatterns = (
    url(r'^$', index),
    url(r'^index', index),
    url(r'^sign', sign),
    url(r'^post', csrf_exempt(post)),
    url(r'^appCallback', csrf_exempt(appCallback)),
    url(r'^accountinfo', csrf_exempt(accountinfo)),
    url(r'^setcallbackfunction', csrf_exempt(setcallbackfunction)),
    url(r'^sendsigrequest', csrf_exempt(sendsigrequest))

)

def convertUTCtoLocal(utcValue):
    if utcValue != None:
        print('nonempty time value given')
        return time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.localtime(float(utcValue)))
    else:
        return "Empty time value given"

def utilTimeStampAndMessage(message):
    ts = time.time()
    ts_readable = convertUTCtoLocal(ts)
    return message + " " + ts_readable

def exploreSignatureRequestResponseObject(responseObject):
    print("********************************************BEGIN exploreSignatureRequestResponseObject********************")
    #listOfSignRequests = []
    print(responseObject.files_url)
    print(" = files_url\n")
    print(responseObject.signing_url)
    print(" = signing_url")
    print(responseObject.details_url)
    print(" = details_url")

    print(type(responseObject.custom_fields))
    print(" = custom_fields - LIST")
    print(len(responseObject.custom_fields))
    for field in responseObject.custom_fields:
        print(field)

    print(responseObject.test_mode)
    print(" =TEST MODE\n")
    print(responseObject.requester_email_address + " =Requester_email_address\n")
    print(responseObject.title)
    print(" =title\n")
    #print(responseObject.message + " =message\n") ----WHY IS THIS CAUSING AN ERROR????
    print(responseObject.has_error)
    print(" =has_error\n")
    print(responseObject.final_copy_uri + " = final_copy_uri\n")
    print(responseObject.subject + " =subject\n")
    print(responseObject.is_complete)
    print(" = is_complete\n")
    print(responseObject.response_data)
    print(" = response_data\n")
    print(responseObject.signatures)
    global _myRecentSigRequest
    for x in responseObject.signatures:
        print(x)
        print(" = x\n")
        print(x.signature_id)
        global lastSigID
        lastSigID =x.signature_id
        #_myRecentSigRequest = x.signature_id
        print(" = x.signature_id\n")
        listOfSignRequests.append(x.signature_id)
        print(x.signer_email_address)
        print(" = x.signer_email_address\n")

        _myDictSignatureRequestID_ToEmail[x.signature_id] = x.signer_email_address
        # {'jack': 4098, 'sape': 4139}

        print(x.signer_name)
        print(" = x.signer_name\n")
        print(x.status_code)
        print(" = x.status_code\n")

        print("--------Begin last reminded at")
        print(x.last_reminded_at)
        print(" = x.last_reminded_at")
        print(convertUTCtoLocal(x.last_reminded_at))
        print("--------END last reminded at")
        print("--------Begin last signed at")
        print(x.signed_at)
        print(" = x.signed_at")
        print(convertUTCtoLocal(x.signed_at))
        print("--------END last signed at")
        print("--------BEGIN last viewed at")
        print(x.last_viewed_at)
        print(" = x.last_viewed_at")
        print(convertUTCtoLocal(x.last_viewed_at))
        global lastSigRequest
        lastSigRequest = responseObject.signature_request_id
        _myRecentSigRequest = responseObject.signature_request_id
        print('lastSigRequest')
        print(lastSigRequest)
        print('lastSigID')
        print(lastSigID)
        print("--------END last viewed at")
    print("********************************************END exploreSignatureRequestResponseObject********************")


application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    timestamp = timeStamped()
    logging.debug(timestamp)
    execute_from_command_line(sys.argv)

