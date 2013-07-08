import re
import cookielib, urllib, urllib2

from core.request.exceptions import NotAuthenticatedException

HTTP_STATUS_OK = 200

class AuthenticatedWebRequest:    
    _login_url = None
    _login_params = None
    _cookies = cookielib.CookieJar()
    _authenticated_checker = None
    
    def __init__(self, login_url, login_params, authenticated_checker):
        self._login_url = login_url
        self._login_params = login_params
        self._authenticated_checker = authenticated_checker
    
    def get_html_response(self, request_url, retry_on_redirect = True):
        html_response = None
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor( \
            self._cookies))
        response = opener.open(request_url)
        
        if self._authenticated_checker.isauthenticated(response = response, \
            cookies = self._cookies):
            html_response = response.read()
        else:
            if retry_on_redirect:
                self.login()
                html_response = self.get_html_response(request_url, False)
            else:
                raise NotAuthenticatedException() 

        return html_response;

    def login(self):
        parameters = self._get_login_parameters() 
        
        data = urllib.urlencode(parameters)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor( \
            self._cookies))
        response = opener.open(self._login_url, data)

    def _get_login_parameters(self):
        parameters = self._login_params.copy()
        html = self._get_login_html_response()
        regex = re.compile( '<input type="hidden" name="(?P<name>.+?)".+?' + \
            'value="(?P<value>.+?)".*?/?>');
        matches = regex.finditer(html)
                
        for match in matches:
            parameters[match.group('name')] = match.group('value')
            
        return parameters

    def _get_login_html_response(self):
        login_html_response = None
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor( \
            self._cookies))
        response = opener.open(self._login_url)        
        login_html_response = response.read()

        return login_html_response
        
class AuthenticatedByCookies:
    _authenticated_cookie_name = None
    
    def __init__(self, authenticated_cookie_name):
        self._authenticated_cookie_name = authenticated_cookie_name
        
    def isauthenticated(self, **kwargs):        
        authenticated = False
        
        for cookie in kwargs['cookies']:
            if cookie.name == self._authenticated_cookie_name:
                authenticated = True
                break
                
        return authenticated