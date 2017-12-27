from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.core.urlresolvers import reverse
from terkeph.models import PhUser
from django.conf import settings
import logging

from terkeph.prohardver import PhSession 

logger = logging.getLogger('terkeph')

def main(request):
    return render(request, 'terkeph/main.html', {
        'robot_userid': 93065,
        'js_api_key': settings.JS_API_KEY,
    })

def heatmap(request):
    users = PhUser.objects.order_by('slug')
    return render(request, 'terkeph/heatmap.html', {
        'users': users,
    })

def parse(request):
    if request.GET.has_key('lat'):
        fragment = '#%s+%s+%s+%s' % (request.GET['lat'], request.GET['lng'], request.GET['zoom'], request.GET['type'])
    else:
        fragment = '#'
    try:
        logger.info('creating ph session')
        ph_session = PhSession(settings.ROBOT_EMAIL, settings.ROBOT_PASS)
        logger.info('ph session created')
        ph_session.parse_privates()
        logger.info('privates parsed')
        # privates parsed
        return HttpResponseRedirect(reverse('main')+fragment)
    except:
        logger.error("could not create ph session")
        return HttpResponseRedirect(reverse('main')+fragment)

def feed(request):
    users = PhUser.objects.order_by('-modified')[:100]
    return render(request, 'terkeph/feed.html', {
        'users': users
    })

def kml(request):
    users = PhUser.objects.order_by('slug')
    return render(request, 'terkeph/kml.html', {
        'users': users
    }, content_type='application/vnd.google-earth.kml+xml')


def json(request):
    users = PhUser.objects.order_by('slug')
    response = render(request, 'terkeph/json.html', {
        'users': users
    }, content_type='application/json; charset=utf-8',)

    response['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
    #response['Content-Length'] = str(len(response.content))
    return response

