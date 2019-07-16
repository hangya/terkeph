from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
from terkeph.models import PhUser
from django.conf import settings
import logging

from terkeph.prohardver import PhSession 

logger = logging.getLogger('terkeph')

def main(request):
    return render(request, 'terkeph/main.html', {
        'robot_userid': 93065,
    })

def parse(request):
    if 'lat' in request.GET:
        fragment = '#%s+%s+%s+%s' % (request.GET.get('lat'), request.GET.get('lng'), request.GET.get('zoom'), request.GET.get('type'))
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
    except Exception as e:
        logger.error("could not create ph session: %s" % type(e))
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
    users = PhUser.objects.order_by('slug').values_list('slug', 'name', 'avatar', 'latlng')
    response = JsonResponse(list(users), safe=False)

    response['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
    return response

