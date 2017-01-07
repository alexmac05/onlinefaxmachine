import sys
import os

from django.conf import settings

DEBUG = os.environ.get('DEBUG', 'on') == 'on'

#SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
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

from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
import json

EVENT_OK_RESP_TOKEN = "Hello API Event Received"

def event_callback(request):
    '''Handles an event callback.
       Extracts event info, prints it out and return a successful response.
    '''
    try:
        data = json.loads(request.POST.get('json'))
        event = data['event']
        print("ehllo")
    except:
        print("HELLO")

    return HttpResponse(EVENT_OK_RESP_TOKEN, content_type="html/text")







def index(request):
    return HttpResponse('Hello World')

urlpatterns = (
    url(r'^$', index),
    url(r'^event_callback', event_callback, name='event_callback'),
)

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
