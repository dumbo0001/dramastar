import re
import urllib2
import traceback
from core.downloaders.base import BaseDownloader
from core.config import configmanager
from core.entities.models import ERROR, EPISODE_STATUS_SNATCHED

class JDownloader(BaseDownloader):  
    ignore_hosts = []
    snatched_domains = []
    
    def __init__(self):    
        self.name = 'core.downloaders.jdownloader'
        self.enabled = configmanager.getboolean(self.name, 'enabled')
        self.use_for = configmanager.get(self.name, 'use_for').split(',')
        self.ignore_hosts = configmanager.getlist(self.name, 'ignore_hosts')
    
    def download(self, filedata, filename, additional_arguments):
        print 'Start snatching episode %r of %r to JDownloader... ' % \
            (additional_arguments, filename)
        return_status = ERROR
        snatched = False        
        
        links = self._get_downloadlinks(filedata, additional_arguments)
        
        if len(links) > 0:
            links_domain_list = [self._get_domain(link) for link in links]
            
            if all(link_domain in self.snatched_domains for link_domain in \
                links_domain_list):
                # All domains of links already snatched.
                # Remove in snatched domains list to be able to snatch again
                for link_domain in links_domain_list:
                    self.snatched_domains.remove(link_domain)

            # Snatch a link
            for link in links:
                domain = self._get_domain(link)            
                if not snatched and domain not in self.snatched_domains:
                    snatched = self._snatch(link)                
                    self.snatched_domains.append(domain)
                    break
            
            if snatched:
                return_status = EPISODE_STATUS_SNATCHED
                print 'Snatched %r' % filename
        else:
            print 'No valid links in file data'
            
        return return_status
        
    def _get_downloadlinks(self, filedata, episode_number):
        links = re.findall( \
            '(?P<url>https?://[^\s]+)', filedata)        
        links = [link for link in links if self._get_domain(link) not in \
            self.ignore_hosts and self._is_link_of_episode_number(link, \
            episode_number)]
        
        return links
        
    def _get_domain(self, link):
        regex = re.compile('https?://(?P<domain>[^\s]+?)/')
        domain = regex.match(link).group('domain')
        
        return domain
        
    def _is_link_of_episode_number(self, link, episode_number):
        is_same = False
        regex = re.compile('https?://[^\s]+?(?P<number>\d+)\..+\.html')
        match = regex.match(link)
        if match:
            number = -1 if match.group('number') == None else \
                int(float(match.group('number')))
            is_same = episode_number == number
                
        return is_same
        
    def _snatch(self, link):
        snatched = False
        try:
            response = urllib2.urlopen('http://' + configmanager.get( \
                self.name, 'host') + '/action/add/links/grabber0/start1/' + \
                link)
            snatch_response = response.read()
            snatched = snatch_response == 'Link(s) added. ("' + link + '"\r\n)'
        except:
            print 'Failed to grab file to JDownloader %r: %r', (link, \
                traceback.format_exc())
            snatched = False
        
        return snatched
        