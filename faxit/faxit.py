import sys
import os
import json
import logging
import datetime
import yaml

from django.conf import settings

creds = yaml.load(open('creds.yml'))


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

    parseData(request)

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
            print("EVENT TYPE is sig")
            sigrequest = data['event']['event_metadata']
            print(sigrequest)

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
        logging.info("IsDraft")
        logging.info(jsonResult['Transaction']['IsDraft'])
        logging.info("TypeCode " + jsonResult['Transaction']['TypeCode'])
        logging.info("StatusCode " + jsonResult['Transaction']['StatusCode'])
        logging.info("ErrorCode")
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
def yourname(request):
    return HttpResponse(request)

urlpatterns = (
    url(r'^$', index),
    url(r'^post', csrf_exempt(post)),
    url(r'^appCallback', csrf_exempt(appCallback)),
    url(r'^yourname', csrf_exempt(yourname))
)

application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    timestamp = timeStamped()
    logging.debug(timestamp)
    execute_from_command_line(sys.argv)

