import sys
import os
import json

from django.conf import settings


DEBUG = os.environ.get('DEBUG', 'on') == 'on'
CSRF_COOKIE_SECURE = False
SECRET_KEY = os.environ.get('SECRET_KEY', '{{ secret_key }}')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

settings.configure(
    DEBUG=DEBUG,
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
from django.views.decorators.http import require_POST

from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse



#@require_POST
@csrf_exempt
def post(request, *args):
    response = HttpResponse("Hello API Event Received")
    parseData(request)

    return response

@csrf_exempt
def parseData(request):

    try:
        #form = cgi.FieldStorage()
        #print(request.body)
        #print("ATTEMPTING STRING DUMP")
        str_response = request.body.decode("utf-8")
        #print(type(str_response))
        #str_response = callbackBytString.decode("utf-8")
        frontChopNumber = str_response.find('{"Transaction"')
        backChopNumber = str_response.find('}}')
        choppedStr_response = str_response[frontChopNumber:backChopNumber + 2]
        jsonResult = json.loads(choppedStr_response)
        print(type(jsonResult))
        print(jsonResult['Transaction']['TypeCode'])

        #The callback for HelloSign
        '''
        #b'------------------------------77934ad02ac3\r\nContent-Disposition: form-data; name="json"\r\n\r\n{"event":{"event_type":"callback_test","event_time":"1484160381","event_hash":"0a7312945ee92921cea0c546d19b8fb180300a62e743647b6b8462bc70c58b67","event_metadata":{"related_signature_id":null,"reported_for_account_id":"f8f805b754bdd2068b8cfb75bb0e2eeb08fbdda2","reported_for_app_id":null,"event_message":null}}}\r\n------------------------------77934ad02ac3--\r\n'
        '''

        #curl -X POST http://localhost:8000/post/ -d '{"foo":"Bar"}'
        #curl -X POST http://f3705785.ngrok.io/post/ -d '{"foo":"Bar"}'


        #The callback for HelloFax


    except:
        print("Unexpected error:", sys.exc_info()[0])

    #print(form)

@csrf_exempt
def index(request):
    return HttpResponse('Hello World')

urlpatterns = (
    url(r'^$', index),
    url(r'^post', csrf_exempt(post)),
)

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
