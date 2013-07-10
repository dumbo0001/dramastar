import re
import urllib2
from core.downloaders.base import BaseDownloader
from core.config import configmanager

class JDownloader(BaseDownloader):
    name = 'core.downloaders.jdownloader'
    use_for = ['directdl']    
    last_domains = []
    
    def download(self, filedata, filename):
        print 'Start Jdownloader download %r... ' % filename
        
        grabbed = False
        ignore_hosts = configmanager.getlist(self.name, 'ignore_hosts')
        links = re.findall('(?P<url>https?://[^\s]+)', filedata)        
        links = [link for link in links if self._get_domain(link) not in \
            ignore_hosts]
        
        # Send to JDownloader
        for link in links:
            domain = self._get_domain(link)
            
            if not grabbed and domain not in self.last_domains:
                self._grab(link)                
                self.last_domains.append(domain)
                grabbed = True
                
        if not grabbed:
            self._grab(link)
            
            domain = self._get_domain(link)          
            self.last_domains = []
            self.last_domains.append(domain)
        
        return True
        
    def _get_domain(self, link):            
        regex = re.compile('https?://(?P<domain>[^\s]+?)/')
        domain = regex.match(link).group('domain')
        
        return domain
        
    def _grab(self, link):
        response = urllib2.urlopen('http://' + configmanager.get(self.name, \
            'host') + '/action/add/links/grabber0/start1/' + link)
        print 'Grabbed %r' % link
        