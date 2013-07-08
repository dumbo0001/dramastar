# -*- coding: utf-8 -*-
from core.entities.models import Show, Episode, SHOW_STATUS_CONTINUING, \
    ShowUrl, EPISODE_STATUS_WANTED, EpisodeUrl
from core.providers import get_providers
from core.repositories.shows import ShowRepository
from core.repositories.episodes import EpisodeRepository
from datetime import datetime

UPDATE_ALL = 0
UPDATE_SHOWS_ONLY = 1

class Updater(object):
    show_repository = ShowRepository()
    episode_repository = EpisodeRepository()
    providers = []
    
    def __init__(self):
        self.providers = get_providers()
    
    def update(self, mode):
        self._update_shows(mode)
        
    def update_show(self, show_id):
        self._update_single_show(show_id = show_id)
        
    def _update_shows(self, mode):
        shows_from_db = self._get_shows_from_db()
        for provider in self.providers:            
            if provider.active:
                shows_from_provider = provider.get_show_list()
                for provider_show in shows_from_provider:
                    show = None
                    show_name = provider_show['name']
                    show_status = provider_show['status']
                    show_url = provider_show['url']
                    show_lastmodified = provider_show['lastmodified']
                    if show_name in shows_from_db:
                        # Existing show
                        show = shows_from_db[show_name]
                        show.status = show_status
                        provider_url_exists = show.urls \
                            .filter_by(provider_id = provider.id) \
                            .count() > 0
                        if not provider_url_exists:
                            db_show_url = ShowUrl(url = provider_show['url'], \
                                show = show, provider_id = provider.id)
                            
                    else:
                        # New show
                        # TODO Add extra property to mark show as duplicate; in this
                        # case search table ShowUrl for correct show to update
                        show = Show(name = show_name, status = show_status, \
                            created = show_lastmodified)
                        show_url = ShowUrl(url = show_url, show = show, \
                            provider_id = provider.id)
                        shows_from_db[show.name] = show
                    self.show_repository.save_show(show)
                    if mode == UPDATE_ALL:
                        self._update_episodes(show)
        
    def _update_single_show(self, show_id):
        show = self.show_repository.get_show(show_id)
        self._update_episodes(show)
        
    def _get_shows_from_db(self):        
        shows = self.show_repository.get_all_shows()
        db_shows = {}
        for show in shows:
            db_shows[show.name] = show
        return db_shows
        
    def _get_shows_from_providers(self):
        show_list = []
        for provider_name in self.providers:
            if self.providers[provider_name].active:
                show_list = show_list + self.providers[provider_name] \
                    .get_show_list()
        return show_list        
        
    def _update_episodes(self, show):
        if show.wanted and (show.status == SHOW_STATUS_CONTINUING or not \
            show.completed):
            print 'Updating episodes of show %r' % show.id
            
            for provider in self.providers:      
                show_url_exists = show.urls \
                    .filter_by(provider_id = provider.id).count() > 0
                if not provider.active or not show_url_exists:
                    print 'provider %r not activated or no show url' % provider.name
                    continue
                    
                print 'Updating episodes of provider %r' % provider.name
                    
                show_url = show.urls \
                    .filter_by(provider_id = provider.id).first()
                    
                episodes_from_provider = provider.get_episode_list( \
                    show_url.url)
                for provider_episode in episodes_from_provider:
                    episode_number = provider_episode['number']
                    episode_number_postfix = provider_episode['number_postfix']
                    episode_airdate = provider_episode['airdate']
                    episode_url = provider_episode['url']
                    episode_name =provider_episode['name']
                    episode = show.episodes \
                        .filter_by(number = episode_number) \
                        .filter_by(number_postfix = episode_number_postfix) \
                        .first()
                    if episode == None:
                        # New episode
                        print 'Adding new episode %r%r' % (episode_number, episode_number_postfix)
                        episode = Episode(number = episode_number, \
                            number_postfix = episode_number_postfix,show_id = \
                            show.id, airdate = episode_airdate, status = \
                            EPISODE_STATUS_WANTED)
                        episode_url = EpisodeUrl(name = episode_name, url = \
                            episode_url, episode = episode, provider_id = \
                            provider.id)
                    else:
                        # Existing episode
                        print 'Updating existing episode %r%r' % (episode_number, episode_number_postfix)
                        provider_url_exists = episode.urls \
                            .filter_by(provider_id = provider.id) \
                            .count() > 0
                        if not provider_url_exists:
                            db_episode_url = EpisodeUrl(name = episode_name, \
                                url = episode_url, episode = episode, \
                                provider_id = provider.id) 
                                
                    self.episode_repository.save_episode(episode)
                    
                print 'Finished updating episodes of provider %r' % provider.name
                
            print 'Finished updating episodes of show %r' % show.id
            