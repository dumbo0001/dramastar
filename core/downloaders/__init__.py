from core import container
from core.entities.models import Downloader as DbDownloader
from core.entities.models import EPISODE_STATUS_DOWNLOADED, \
    EPISODE_STATUS_WANTED
from core.downloaders.blackhole import BlackHole
from core.downloaders.jdownloader import JDownloader
from core.providers import get_providers
from core.repositories.downloaders import DownloaderRepository
from core.repositories.providers import ProviderRepository
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
    
    _sync_downloaders_in_db(loaded_downloaders)
    container.downloaders = loaded_downloaders
    
def _sync_downloaders_in_db(loaded_downloaders):
    downloader_repository = DownloaderRepository()
    provider_repository = ProviderRepository()
    downloaders_from_db = _get_downloaders_from_db()
            
    for loaded_downloader in loaded_downloaders:
        if loaded_downloader.name in downloaders_from_db:
            downloader = downloaders_from_db[loaded_downloader.name]
        else:
            # Insert downloader to db
            # TODO Set default active state to False
            print 'Adding downloader %r' % loaded_downloader.name
            downloader = DbDownloader(name = loaded_downloader.name, 
                active = True)
            for use_for in loaded_downloader.use_for:
                use_for_providers = _get_use_for_providers(use_for)
                for use_for_provider in use_for_providers:
                    provider = provider_repository.get_provider( \
                        use_for_provider.id)
                    downloader.providers.append(provider)
            downloader_repository.save_downloader(downloader)
        loaded_downloader.active = downloader.active
        loaded_downloader.id = downloader.id
        loaded_downloader.use_for

def _get_downloaders_from_db():
    downloader_repository = DownloaderRepository()
    downloaders_from_db = downloader_repository.get_downloaders()
    db_downloaders = {}
    for downloader in downloaders_from_db:
        db_downloaders[downloader.name] = downloader
    return db_downloaders
    
def _get_use_for_providers(use_for):
    use_for_providers = []
    providers = get_providers()
    for provider in providers:
        print 'Looking up %r in provider %r' % (use_for, provider.name)
        if use_for in provider.name:
            print '%r found in provider %r' % (use_for, provider.name)
            use_for_providers.append(provider)
        
    return use_for_providers    
    
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
        episode = self.episode_repository.get_episode(episode_id)
        
        if episode == None:
            print 'Episode %r does not exists' % episode_id
            
        episode_urls = self._get_sorted_urls(episode.urls)
        for episode_url in episode_urls:
            print 'Downloading %r of %r' % (episode_url.url, episode_url.provider.name)
            provider_name = episode_url.provider.name
                
            if not any(x.name == provider_name for x in self.providers):
                print 'Provider %r not loaded' % provider_name
                continue
            
            provider = next(x for x in self.providers if x.name == provider_name)
                
            for downloader in self.downloaders:
                if not downloader.active:
                    print 'Downloader %r not active' % downloader.name
                    continue
                
                if not any(x in provider_name for x in downloader.use_for):
                    print 'Downloader %r not in use for provider %r' % (downloader.name, provider_name)
                    continue
            
                # TODO Add retry mechanism and skip to next downloader
                filedata = provider.get_filedata(episode_url.url)
                success = downloader.download(filedata, episode_url.name)
                break
                
            if success:
                episode = self.episode_repository.get_episode(episode_id)
                episode.status = EPISODE_STATUS_DOWNLOADED
                self.episode_repository.save_episode(episode)
                break
        
        return success
                
    def _get_sorted_urls(self, urls):
        urls_order_list = [self._get_provider_order(x.provider_id) for x in \
            urls]
        urls_with_order = zip(urls_order_list, urls)
        urls_with_order.sort()
        sorted_urls_order_list, sorted_urls = zip(*urls_with_order)
        
        return sorted_urls
    
    def _get_provider_order(self, provider_id):
        order = 99
        provider = next(x for x in self.providers if x.id == provider_id)
        
        if not provider == None:
            order = provider.order
        
        return order