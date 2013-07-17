# -*- coding: utf-8 -*-
import logging
from core.entities.models import Show, Episode, SHOW_STATUS_CONTINUING, \
    ShowUrl, EPISODE_STATUS_WANTED, EpisodeUrl
from core.providers import get_providers
from core.repositories.shows import ShowRepository
from core.repositories.episodes import EpisodeRepository
from datetime import datetime

UPDATE_ALL = 0
UPDATE_SHOWS_ONLY = 1

log = logging.getLogger(__name__)

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
        log.info('Updating shows, mode = %s' % 'all' if mode == UPDATE_ALL \
            else 'show only')
        shows_from_db = self._get_shows_from_db()
        for provider in self.providers:            
            if provider.enabled:
                shows_from_provider = provider.get_show_list()
                log.info('Found %d shows' % len(shows_from_provider))
                log.info('Updating...')
                for provider_show in shows_from_provider:
                    show = None
                    show_name = provider_show['name']
                    show_status = provider_show['status']
                    show_url = provider_show['url']
                    show_lastmodified = provider_show['lastmodified']
                    if show_name in shows_from_db:
                        # Existing show
                        log.debug('Show %s exists. Updating...' % show_name)
                        show = shows_from_db[show_name]
                        show.status = show_status
                        provider_url_exists = show.urls \
                            .filter_by(provider = provider.name) \
                            .count() > 0
                        if not provider_url_exists:
                            log.info('Adding new show url to show...' % \
                                show_name)
                            db_show_url = ShowUrl(url = provider_show['url'], \
                                show = show, provider = provider.name)
                            
                    else:
                        # New show
                        log.info('Show %s not found. Adding...' % show_name)
                        # TODO Add extra property to mark show as duplicate; in this
                        # case search table ShowUrl for correct show to update
                        show = Show(name = show_name, status = show_status, \
                            created = show_lastmodified)
                        show_url = ShowUrl(url = show_url, show = show, \
                            provider = provider.name)
                        shows_from_db[show.name] = show
                    self.show_repository.save_show(show)
                    if mode == UPDATE_ALL:
                        self._update_episodes(show)
                        
        log.info('Finished updating shows...')
        
    def _update_single_show(self, show_id):
        show = self.show_repository.get_show(show_id)
        log.info('Updating show %s...' % show.name)
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
            if self.providers[provider_name].enabled:
                show_list = show_list + self.providers[provider_name] \
                    .get_show_list()
        return show_list        
        
    def _update_episodes(self, show):
        if show.wanted and (show.status == SHOW_STATUS_CONTINUING or not \
            show.completed):
            log.info('Updating episodes of show %s' % show.name)
            for provider in self.providers:      
                show_url_exists = show.urls \
                    .filter_by(provider = provider.name).count() > 0
                    
                if not provider.enabled or not show_url_exists:
                    log.info('Provider %s disabled or doesn''t provide show' \
                        % provider.name)
                    continue
                    
                log.info('Updating episodes of provider %s' % provider.name)
                    
                show_url = show.urls \
                    .filter_by(provider = provider.name).first()
                    
                episodes_from_provider = provider.get_episode_list( \
                    show_url.url)
                log.info('Found %d episodes' % len(episodes_from_provider))
                log.info('Updating...')
                for provider_episode in episodes_from_provider:
                    episode_number = provider_episode['number']
                    episode_number_postfix = provider_episode['number_postfix']
                    episode_airdate = provider_episode['airdate']
                    episode_url = provider_episode['url']
                    episode_name = provider_episode['name']
                    episode = show.episodes \
                        .filter_by(number = episode_number) \
                        .filter_by(number_postfix = episode_number_postfix) \
                        .first()
                    if episode == None:
                        # New episode
                        log.info('Episode %r%s not found. Adding...' % \
                            (episode_number, episode_number_postfix))
                        episode = Episode(number = episode_number, \
                            number_postfix = episode_number_postfix,show_id = \
                            show.id, airdate = episode_airdate, status = \
                            EPISODE_STATUS_WANTED)
                        episode_url = EpisodeUrl(name = episode_name, url = \
                            episode_url, episode = episode, provider = \
                            provider.name)
                    else:
                        # Existing episode
                        log.debug('Episode %r%s exists. Updating...' % (\
                            episode_number, episode_number_postfix))
                        provider_url_exists = episode.urls \
                            .filter_by(provider = provider.name) \
                            .count() > 0
                        if not provider_url_exists:
                            log.info('Adding new episode url to episode...' % \
                                episode_name)
                            db_episode_url = EpisodeUrl(name = episode_name, \
                                url = episode_url, episode = episode, \
                                provider = provider.name)
                        else:
                            log.debug('Nothing to update...')
                                
                    self.episode_repository.save_episode(episode)
                
            log.info('Finished updating episodes of show %s' % show.name)
        else:
            log.debug('No episodes to update for show %s.' % show.name + \
                'Show not wanted or already completed....' )