from django.template.loader import render_to_string
import re
import requests
import logging
import decimal
from terkeph.models import PhUser

logger = logging.getLogger('terkeph')

class PhPrivateMessage:

    def __init__(self, session, sender, content):
        
        self.session = session
        self.sender = sender
        self.content = re.sub('<br/>', '\n', content)
        logger.debug('private content: %s' % self.content)

    def get_value(self, keyname):
        logger.info('getting %s' % (keyname))
        try:
            value = re.search(r'^'+keyname+'=(.*)$', self.content, re.M).group(1)
            logger.info('value: %s' % value)
        except Exception as e:
            logger.error('exception: %s' % e)
            value = ''
        logger.info('key: %s, value: %s' % (keyname, value))
        return value
    
    def error(self, message):
        logger.info('Error while parsing private msg from %s: %s\n%s' % (self.sender.slug, message, self.content))
        
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
                    self.sender.latlng = self.get_value('point')
                    logger.debug('latlng: %s' % self.sender.latlng)
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
        self.cookies = ''
        self.login()
        
    def login(self):
        result = requests.get("https://prohardver.hu/privatok/listaz.php")
        self.cookies = result.cookies
        result = requests.get("https://prohardver.hu/privatok/listaz.php", cookies=self.cookies)
        fid = re.search('<input type="hidden" name="fidentifier" value="([^"]*)"/>', result.text).group(1)
        form_fields = {
            'fidentifier': (None, fid),
            'email': (None, self.email),
            'pass': (None, self.password),
            'all': (None, '1'),
            'stay': (None, '1'),
            'no_ip_check': (None, '1'),
            'leave_others': (None, '1'),
        }
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        logger.info(form_fields)
        try:
            result = requests.post("https://prohardver.hu/muvelet/hozzaferes/belepes.php", files=form_fields, cookies=self.cookies, headers=headers)
            logger.info('login result: %s' % result)
            logger.info('login result: %s' % result.text)
            self.cookies = result.cookies
        except Exception as error:
            logger.info('urlopen error: %s' % error)
            raise
          
        
    def get_page(self, path='/'):
        "returns the content of an authenticated page"
        logger.info('fetching %s' % (path))
        try:
            result = requests.get("https://prohardver.hu%s" % path, cookies=self.cookies)
            logger.info('result: %s' % result)
            return result.text
        except Exception as error:
            logger.info('get_page error: ' + error)

    def send_private(self, recepient, template_name, values):
        logger.debug('sending private to %s' % recepient)
        page = self.get_page("/privat/%s/kuld.php" % recepient.slug)
        fid = re.search('<input type="hidden" name="fidentifier" value="([^"]*)"/>', page).group(1)
        message = render_to_string('messages/%s.txt' % template_name, values)
        logger.debug('message: %s' % message)
        form_fields = {
            "fidentifier": (None, fid),
            "mce_0": (None, ""),
            "content": (None, message)
        }
        logger.debug('form data: %s' % form_fields)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            logger.debug("creating private send request")
            result = requests.post("https://prohardver.hu/muvelet/privat/uj.php?dstid=%s" % recepient.uid, files=form_fields, cookies=self.cookies, headers=headers)
            logger.debug('send private result: %s, %s' % (result, result.text))
            logger.debug("sending to uid %s" % recepient.uid)
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
            r'<li class="media thread-unread">\s*<div class="media-body">\s*<div class="col thread-face">\s*'
            +'<img src="/dl/faces/small/(?P<avatar>[^"]*?).gif" alt="" />\s*</div>\s*<div class="col thread-title-user">\s*'
            +'<a href="/privat/(?P<slug>.*?)/listaz.php(?P<offset>.*?)">(?P<name>.*?)</a>\s*</div>\s*'
            +'<div class="col thread-num-msgs d-none d-md-block">(?P<unread>\d+) db</div>\s*'
            +'<div class="col thread-num-msgs d-none d-md-block">(?P<count>\d+) db</div>\s*'
            +'<div class="col thread-time d-none d-lg-block">(?P<last>[\d :-]+)</div>\s*<div class="col thread-action">\s*'
            +'<button class="btn btn-xs" data-action-privconv-del="/muvelet/privbesz/torol.php\?oth_usrid=(?P<userid>\d*)',
            page, re.DOTALL)
        
        unread_sender_list = []
        for unread_sender in unread_senders:
            userdict = unread_sender.groupdict()
            logger.debug('new private from %s' % userdict['slug'])
            userdict['name'] = userdict['name']
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
                  avatar = userdict['avatar']
                )

            
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
            unread_messages = re.findall(r'<li class="media msg-featured">.*?<p class="mgt\d">(.*?)</p>', page, re.DOTALL)
            for unread_message in unread_messages:
                logger.debug('unread message: %s' % unread_message)
                ph_message = PhPrivateMessage(self, sender, unread_message)
                ph_message.parse()

