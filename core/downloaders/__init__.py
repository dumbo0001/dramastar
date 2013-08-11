import logging
from core import container
from core.entities.models import EPISODE_STATUS_SNATCHED, \
    EPISODE_STATUS_WANTED, EPISODE_STATUS_DOWNLOADED
from core.downloaders.blackhole import BlackHole
from core.downloaders.jdownloader import JDownloader
from core.providers import get_providers
from core.repositories.episodes import EpisodeRepository
from core.repositories.shows import ShowRepository

log = logging.getLogger(__name__)

container.downloaders = None

def get_downloaders():
    if container.downloaders == None:
        _load_downloaders()
    return container.downloaders

def _load_downloaders():
    log.info('Loading downloaders...')
    # TODO load downloader modules
    loaded_downloaders = [ BlackHole(), JDownloader()]
    
    container.downloaders = loaded_downloaders 
    log.info('Finished loading downloaders...')
    
class Downloader(object):    
    downloaders = []
    providers = []
    episode_repository = EpisodeRepository()
    show_repository = ShowRepository()
    
    def __init__(self):
        self.downloaders = get_downloaders()
        self.providers = get_providers()
        
    def download_wanted_shows(self):
        wanted_shows = self.show_repository.get_wanted_shows()
        
        if len(wanted_shows) == 0:
            log.info('Nothing to download. No wanted shows...')
            pass
            
        log.info('Downloading wanted shows...')
        for show in wanted_shows:
            self.download_show(show.id)
        log.info('Finished downloading wanted shows...')
        
    def download_show(self, show_id):
        show = self.show_repository.get_show(show_id)
        
        if show == None:
            log.info('Show %r not found...' % show_id)
            pass
        
        if not show.wanted:
            log.info('Show %s not in wanted list' % show.name)
            pass
            
        wanted_episodes = show.episodes.filter_by(status = \
            EPISODE_STATUS_WANTED)
            
        log.info('Downloading wanted episodes...')
        for episode in wanted_episodes:
            self.download_episode(episode.id)
        log.info('Finished downloading wanted episodes...')
            
    def download_episode(self, episode_id):
        success = False
        episode = self.episode_repository.get_episode(episode_id)
        
        if episode == None:
            log.info('Episode %r not found' % episode_id)
            pass
            
        log.info('Downloading %s episode %r%s' % (episode.show.name, \
            episode.number, episode.number_postfix))
        episode_urls = self._get_sorted_urls(episode.urls)
        for episode_url in episode_urls:
            provider_name = episode_url.provider
                
            if not any(x.name == provider_name for x in self.providers):
                log.info('Provider %r not loaded for episode. Skipping...' % \
                    provider_name)
                continue
                
            provider = next(x for x in self.providers if x.name == \
                provider_name)
                
            for downloader in self.downloaders:
                if not downloader.enabled:
                    log.info('Downloader %s not enabled. Skipping...' % \
                        downloader.name)
                    continue
                
                if not any(x in provider_name for x in downloader.use_for):
                    log.info('Downloader %s not in use ' % downloader.name + \
                        'for provider %s. Skipping...' %  provider_name)
                    continue
                
                log.info('Downloading using %s' % episode_url.provider)
                log.info('Getting file data of provider %s from %s' % \
                    (episode_url.provider, episode_url.url) )
            
                # TODO Add retry mechanism and skip to next downloader
                filedata = provider.get_filedata(episode_url.url)
                episode_status = downloader.download(filedata, \
                    episode_url.name, episode.number)
                break
                
            if episode_status == EPISODE_STATUS_SNATCHED or episode_status == \
                EPISODE_STATUS_DOWNLOADED:
                episode = self.episode_repository.get_episode(episode_id)
                episode.status = episode_status
                self.episode_repository.save_episode(episode)
                succes = True
                log.info('Episode succesfully snatched/downloaded...')
                break
        
        return success
                
    def _get_sorted_urls(self, urls):
        urls_order_list = [self._get_provider_order(x.provider) for x in \
            urls]
        urls_with_order = zip(urls_order_list, urls)
        urls_with_order.sort()
        sorted_urls_order_list, sorted_urls = zip(*urls_with_order)
        
        return sorted_urls
    
    def _get_provider_order(self, provider_name):
        order = 99
        provider = next(x for x in self.providers if x.name == provider_name)
        
        if not provider == None:
            order = provider.order
        
        return order