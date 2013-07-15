 # -*- coding: utf-8 -*-
from core.providers.base import BaseProvider
from core.providers.parsers.hdzone import ShowListParser, \
    EpisodeListParser
from core.request.authenticated import AuthenticatedWebRequest, \
    AuthenticatedByCookies
from core.config import configmanager

class HdZone(BaseProvider):
    _show_list_url = 'http://www.hdzone.org/forumdisplay.php?fid=134'  
    _show_name_regex = u'(?P<title>.+?)\sCH\s\d{2,3}(\s-\sCH\s\d{2,3})?' + \
        u'([AB])?\s(大結局|全集完)?'
    _show_ended_regex = u'(?P<ended>大結局|全集完)'
    _episode_regex = u'^.+\sCH\s(?P<number>\d+)(\s?end)?(?P<number_postfix>[AB' + \
        '])?\.(?P<extension>.+)$'
        
    _authenticated_request = None
    _episode_list_parser = None
    _show_list_parser = None
    
    def __init__(self):
        self.name = 'core.providers.directdl.hdzone'
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
        html = self._authenticated_request.get_html_response(self._show_list_url)
        
        return self._show_list_parser.parse_shows(html)
        
    def get_episode_list(self, url):
        html = self._authenticated_request.get_html_response(url)
        
        return self._episode_list_parser.parse_episode_list(html)

    def get_filedata(self, url):
        data = self._authenticated_request.get_html_response(url)
        
        return data