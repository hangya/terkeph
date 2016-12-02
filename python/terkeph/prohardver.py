# -*- coding:utf-8 -*- 

from django.template.loader import get_template
from django.template import Context
import re
#import os
import urllib
import urllib2
import logging
import decimal
#from django.conf import settings
from terkeph.models import PhUser

logger = logging.getLogger('terkeph')

class PhPrivateMessage:

    def __init__(self, session, sender, content):
        
        self.session = session
        self.sender = sender
        self.content = re.sub('<br />', '\n', content)
        logger.debug('private content: %s' % self.content)

    def get_value(self, keyname):
        try:
            value = re.search(r'^'+keyname+'=(.*)$', self.content, re.M).group(1)
        except AttributeError:
            value = ''
        return value
    
    def error(self, message):
        logger.info('Error while parsing private msg from %s: %s\n%s' % (self.sender.slug, message, unicode(self.content.decode('utf-8'))))
        
    def parse(self):
        logger.info('parse function')
        applications = ('map',)
        application = self.get_value('app')

        if not applications.__contains__(application):
            self.session.send_private(self.sender, 'undefined', {'user': self.sender, 'content': self.content})
            self.error('undefined application, sender notified.', 'debug')
        
        if application == 'map':
            actions = ('add', 'del')
            action = self.get_value('action')
            if not actions.__contains__(action):
                self.error('undefined action')
            
            if action == 'add':
                logger.info('start add')
                try:
                    lat, lng = self.get_value('point').split(',')
                    logger.debug('lat: %s, lng: %s' % (lat, lng))
                    self.sender.point_lat = decimal.Decimal(lat)
                    self.sender.point_lng = decimal.Decimal(lng)
                    logger.debug('coordinates set to %s %s' % (self.sender.point_lat, self.sender.point_lng))
                    self.sender.save()
                    logger.debug('%s saved' % self.sender)
                    self.session.send_private(self.sender, 'add', {'user': self.sender})
                    logger.debug('Added new user: %s', self.sender.slug)
                except ValueError:
                    self.error('invalid value')

            elif action == 'del':
                logger.info('start del')
                logger.info('sender: %s' % self.sender)
                if self.sender.pk:
                    logger.info('deleting saved user')
                    self.session.send_private(self.sender, 'del', {'user': self.sender})
                    self.sender.delete()
                    logger.debug('Deleted user: %s', self.sender.slug)
                else:
                    logger.info('unsaved user, nothing to delete')
                    self.session.send_private(self.sender, 'undel', {'user': self.sender})
                    logger.debug('Deleted user: %s (was not there)', self.sender.slug)




class PhSession:
    
    def __init__(self, email, password):
        "logs in, creates self.cookie used for authentication"
        self.email = email
        self.password = password
        self.cookie = ''
        self.login()
        
    def login(self):
        form_fields = {
            'email': self.email,
            'pass': self.password,
            'stay': '1',
            'no_ip_check': '1',
            'leave_others': '1',
        }
        form_data = urllib.urlencode(form_fields)
        try:
          request = urllib2.Request(url="https://prohardver.hu/muvelet/hozzaferes/belepes.php")
          request.add_header('Content-Type', 'application/x-www-form-urlencoded')
          request.add_data(form_data)
          result = urllib2.urlopen(request)
          for header in result.info().headers:
            if header.startswith('Set-Cookie'):
              self.cookie += header.split(':')[1].split(';')[0]+'; '
        except urllib2.URLError, error:
          logger.info('urlopen error: %s' % error)
          raise
          
        
    def get_page(self, path='/'):
        "returns the content of an authenticated page"
        logger.info('fetching %s with cookie %s' % (path, self.cookie))
        request = urllib2.Request(url="https://prohardver.hu%s" % path)
        request.add_header('Cookie', self.cookie)
        result = urllib2.urlopen(request)
        return result.read()

    def send_private(self, recepient, template_name, values):
        #logger.debug('sending private to %s' % recepient)
        template = get_template('messages/%s.txt' % template_name)
	message = template.render(Context(values))
        try:
          logger.debug('message: %s' % message.encode('utf-8'))
	  form_fields = {"content": message.encode('utf-8')}
	  form_data = urllib.urlencode(form_fields)
          logger.debug('form data: %s' % form_data)
	except Exception as e:
	  logger.error('exception! %s' % e)
	try:
          logger.debug("creating private send request")
	  request = urllib2.Request(url="https://prohardver.hu/muvelet/privat/uj.php?dstid=%s" % recepient.uid)
          logger.debug("sending to uid %s" % recepient.uid)
	  request.add_header('Content-Type', 'application/x-www-form-urlencoded')
          request.add_header('Cookie', self.cookie)
          request.add_data(form_data)
          result = urllib2.urlopen(request)
	except:
	  logger.error('could not send private to %s' % recepient.slug)
 
    def privates_unread_senders(self):
        "which users sent new messages"
        
        try:
            page = self.get_page('/privatok/listaz.php')
            logger.debug('private message list received')
        except: # urlfetch.DownloadError:
            logger.error('Could not download new private message senders list')
            return [] # could not download unread private senders, return no users
        
        unread_senders = re.finditer(
                r'<tr class=".*?feat">\s*<td class="face"><img src="/dl/faces/small/(?P<avatar>[^"]*?).gif" alt="" /></td>\s*'
                +'<td class="title"><a href="/privat/(?P<slug>.*?)/listaz.php(?P<offset>.*?)">(?P<name>.*?)</a></td>\s*'
                +'<td class="num_new">(?P<unread>\d+) db</td>.*?'
                +'<a href="/muvelet/privbesz/torol.php\?oth_usrid=(?P<userid>\d*)&.*?</tr>', 
                page, re.DOTALL)
        
        unread_sender_list = []
        for unread_sender in unread_senders:
            userdict = unread_sender.groupdict()
            logger.debug('new private from %s' % userdict['slug'])
            userdict['name'] = unicode(userdict['name'].decode('utf-8'))
            try:
              ph_user = PhUser.objects.get(uid=userdict['userid'])
              # update values
              logger.debug('updating %s' % userdict['slug'])
              ph_user.slug = userdict['slug']
              ph_user.name = userdict['name']
              ph_user.avatar = userdict['avatar']
            except Exception as e: # create user if not exist
              logger.debug('exception: %s' %e)
              logger.debug('creating %s' % userdict['slug'])
              ph_user = PhUser(
                uid = int(userdict['userid']),
                slug = userdict['slug'],
                name = userdict['name'],
                avatar = userdict['avatar'])
 
            
            #ph_user.put() # kiszedve, nem biztos hogy letre akarjuk hozni
            
            unread_sender_list.append((ph_user, userdict['offset']))
            
        return unread_sender_list
    
                
    def parse_privates(self):
        logger.debug('Parsing private messages')
        senders = self.privates_unread_senders()
        logger.debug('Senders identified')
        for (sender, offset) in senders:
            logger.debug('unread private from %s' % sender.slug)
            #sender.parse_privates(self, offset)
	    try:
	      page = self.get_page("/privat/%s/listaz.php%s" % (sender.slug, offset))
	    except:
	      logger.error('could not download privates')
	    unread_messages = re.findall(r'<div class="msg flc isnew">.*?<p class="mgt\d">(.*?)</p>', page, re.DOTALL)
	    for unread_message in unread_messages:
              logger.debug('unread message: %s' % unread_message)
	      ph_message = PhPrivateMessage(self, sender, unread_message)
	      ph_message.parse()

