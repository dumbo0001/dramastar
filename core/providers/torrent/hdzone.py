 # -*- coding: utf-8 -*-
import logging
from core.providers.base import BaseProvider
from core.providers.parsers.hdzone import ShowListParser, \
    EpisodeListParser
from core.request.authenticated import AuthenticatedWebRequest, \
    AuthenticatedByCookies
from core.config import configmanager

log = logging.getLogger(__name__)

class HdZone(BaseProvider):
    _show_list_url = 'http://www.hdzone.org/forumdisplay.php?fid=21'
    _show_name_regex = u'(ATV)?(?P<title>.+?)(\d{1,3}|\d{1,3}完|全集.+完)-' + \
        '\d{4}-\d{1,2}-\d{1,2}-'
    _show_ended_regex = u'(\d{1,3}完|全集.+完)'
    _episode_regex = u'^.+?(-)?(?P<number>\d+)(end|完)?(?P<number_postfix>' + \
        '[AB])?-(?P<airdate>\d{4}-\d{1,2}-\d{1,2})\.(?P<extension>.+)$'
        
    _authenticated_request = None    
    _episode_list_parser = None
    _show_list_parser = None
    
    def __init__(self):
        self.name = 'core.providers.torrent.hdzone'
        self.enabled = configmanager.getboolean(self.name, 'enabled')
        self.order = configmanager.getint(self.name, 'order')
        
        self._show_list_parser = ShowListParser( \
            configmanager.get(self.name, 'author'), \
            self._show_name_regex, self._show_ended_regex)
        self._episode_list_parser = EpisodeListParser(self._episode_regex)
        
        authenticated_checker = AuthenticatedByCookies('cdb_auth')
        login_url = 'http://hdzone.org/logging.php?action=login'
        login_params = {
            'username' : configmanager.get(self.name, 'username'),
            'password' : configmanager.get(self.name, 'password'),
            'cookietime' : '2592000',
            'loginsubmit' : '提   交'
        }
        self._authenticated_request = AuthenticatedWebRequest( \
            login_url, login_params, authenticated_checker)
        
    def get_show_list(self):
        log.info('Retrieving show list of provider %s' % self.name)
        html = self._authenticated_request.get_html_response(self._show_list_url)
        
        return self._show_list_parser.parse_shows(html)
        
    def get_episode_list(self, url):
        log.info('Retrieving episode list of provider %s' % self.name)
        html = self._authenticated_request.get_html_response(url)
        
        return self._episode_list_parser.parse_episode_list(html)

    def get_filedata(self, url):
        data = self._authenticated_request.get_html_response(url)
        
        return data
