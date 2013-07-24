# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from core.entities.models import SHOW_STATUS_CONTINUING, SHOW_STATUS_ENDED
from datetime import date, datetime
import re
import string

class ShowListParser(object):
    _author = None
    _name_regex = None
    _ended_regex = None
    
    def __init__(self, author, name_regex, ended_regex):
        self._author = author
        self._name_regex = name_regex
        self._ended_regex = ended_regex
        
    def parse_shows(self, html):
        shows = []
        soup = BeautifulSoup(html)
        
        tr_tags = [img.find_parent('tr') for img in soup('img', \
            src = re.compile('pin_1\.gif'))]
               
        for tr_tag in tr_tags:
            try:
                author = self._parse_author(tr_tag)
                if author != self._author:
                    continue
                name = self._parse_name(tr_tag)
                url = self._parse_url(tr_tag)
                status = self._parse_status(tr_tag)	
                lastmodified = self._parse_lastmodified(tr_tag)
                if name != '' and url != '':
                    shows.append({
                        'name': name.strip(),
                        'url' : url,
                        'status' : status,
                        'lastmodified' : lastmodified
                    })
            except AttributeError:
                continue
            
        return shows
        
    def _parse_author(self, tr_tag):
        return tr_tag.find('td', class_ = 'f_author').find('a').string
        
    def _parse_name(self, tr_tag):  
        regex = re.compile(self._name_regex)
        
        name_raw = tr_tag.find('td', class_ = 'f_title').find('a').string
        match = regex.match(name_raw)     
         
        name = ''
        if match:
            name = match.group('title')
               
        return name
        
    def _parse_status(self, tr_tag):  
        regex = re.compile(self._ended_regex)
        
        name_raw = tr_tag.find('td', class_ = 'f_title').find('a').string
        match = regex.search(name_raw)
                
        status = SHOW_STATUS_CONTINUING
        if match:
            status = SHOW_STATUS_ENDED
                           
        return status
        
    def _parse_url(self, tr_tag):
        return 'http://www.hdzone.org/' + tr_tag.find('td', class_ = \
            'f_title').find('a').get('href')
        
    def _parse_lastmodified(self, tr_tag):        
        regex = re.compile(u'(?P<year>\d{4})年(?P<month>\d{1,2})月' + \
            u'(?P<day>\d{1,2})日')
        
        lastmodified_raw = tr_tag.find('td', class_ = 'f_last').find('a') \
            .string
        match = regex.match(lastmodified_raw)
        lastmodified = datetime(int(float(match.group('year'))), \
            int(float(match.group('month'))), int(float(match.group('day'))), \
            0, 0)
            
        return lastmodified
        
class EpisodeListParser():
    DOWNLOAD_URL_FORMAT = 'http://www.hdzone.org/attachment.php?aid=%s'
    _episode_regex = None
    
    def __init__(self, episode_regex):
        self._episode_regex = episode_regex
    
    def parse_episode_list(self, html):
        episodes = []
        soup = BeautifulSoup(html)
        
        div_tags = soup('div', class_ = 't_attachlist')
        for div_tag in div_tags:
            try:
                regex = re.compile(self._episode_regex, re.I)
                match = regex.match(div_tag.find('a', class_ = 'bold').string)
                
                if match:
                    name = self._parse_name(div_tag)
                    number = int(float(match.group('number')))
                    number_end = number if \
                        'number_end' not in match.groupdict() \
                        or match.group('number_end') == None \
                        else int(float(match.group('number_end')))
                    number_postfix = match.group('number_postfix') or ''
                    airdate = self._parse_airdate(div_tag)
                    aid = self._parse_aid(div_tag)
                    url = self.DOWNLOAD_URL_FORMAT % aid
                    for num in range(number, number_end + 1):
                        episodes.append({
                            'name': name,
                            'url': url,
                            'number' : num,
                            'number_postfix' : number_postfix,
                            'airdate' : airdate
                        })
            except AttributeError:
                continue
        
        return episodes
        
    def _parse_name(self, div_tag):
        return div_tag.find('a', class_ = 'bold').string
        
    def _parse_airdate(self, div_tag):
        date_string = None
        for string in  div_tag.find('div', \
            class_ = ['right', 'smalltxt']).stripped_strings:
            date_string = string
            break
        
        regex = re.compile(u'(?P<year>\d{4})年(?P<month>\d{1,2})月' + \
            u'(?P<day>\d{1,2})日')
        match = regex.match(date_string)
        airdate = datetime(int(float(match.group('year'))), \
            int(float(match.group('month'))), int(float(match.group('day'))), \
            0, 0)
            
        return airdate
        
    def _parse_aid(self, div_tag):
        onclick = div_tag.find('a', class_ = 'bold')['onclick']
        
        regex = re.compile('.+@(?P<ep_id>\d+)')
        match = regex.match(onclick, re.I)
        
        ep_id = int(float(match.group('ep_id')))
        return int((ep_id - 15)/51)

