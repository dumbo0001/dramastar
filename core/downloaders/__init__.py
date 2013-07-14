from core import container
from core.entities.models import EPISODE_STATUS_SNATCHED, \
    EPISODE_STATUS_WANTED, EPISODE_STATUS_DOWNLOADED
from core.downloaders.blackhole import BlackHole
from core.downloaders.jdownloader import JDownloader
from core.providers import get_providers
from core.repositories.episodes import EpisodeRepository
from core.repositories.shows import ShowRepository

container.downloaders = None

def get_downloaders():
    if container.downloaders == None:
        print 'Loading downloaders...'
        _load_downloaders()
    print 'Finished loading downloaders...'
    return container.downloaders

def _load_downloaders():
    # TODO load downloader modules
    loaded_downloaders = [ BlackHole(), JDownloader()]
    
    container.downloaders = loaded_downloaders 
    
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
        
        if wanted_shows.count() == 0:
            print 'No wanted shows'
            
        for show in wanted_shows:
            self.download_show(show.id)
        
    def download_show(self, show_id):
        show = self.show_repository.get_show(show_id)
        
        if show == None:
            print 'Show %r does not exist' % show_id
        
        if not show.wanted:
            print 'Show %r not in wanted list' % show_id
            
        wanted_episodes = show.episodes.filter_by(status = \
            EPISODE_STATUS_WANTED)
            
        for episode in wanted_episodes:
            self.download_episode(wanted_episode.id)
            
    def download_episode(self, episode_id):
        success = False
        episode = self.episode_repository.get_episode(episode_id)
        
        if episode == None:
            print 'Episode %r does not exists' % episode_id
            
        episode_urls = self._get_sorted_urls(episode.urls)
        for episode_url in episode_urls:
            print 'Downloading %r of %r' % (episode_url.url, episode_url.provider)
            provider_name = episode_url.provider
                
            if not any(x.name == provider_name for x in self.providers):
                print 'Provider %r not loaded' % provider_name
                continue
            
            provider = next(x for x in self.providers if x.name == provider_name)
                
            for downloader in self.downloaders:
                if not downloader.enabled:
                    print 'Downloader %r not enabled' % downloader.name
                    continue
                
                if not any(x in provider_name for x in downloader.use_for):
                    print 'Downloader %r not in use for provider %r' % (downloader.name, provider_name)
                    continue
            
                # TODO Add retry mechanism and skip to next downloader
                filedata = provider.get_filedata(episode_url.url)
                episode_status = downloader.download(filedata, episode_url.name)
                break
                
            if episode_status == EPISODE_STATUS_SNATCHED or episode_status == \
                EPISODE_STATUS_DOWNLOADED:
                episode = self.episode_repository.get_episode(episode_id)
                episode.status = episode_status
                self.episode_repository.save_episode(episode)
                succes = True
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