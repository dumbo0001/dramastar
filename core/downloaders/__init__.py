from core import container
from core.entities.models import Downloader as DbDownloader
from core.entities.models import EPISODE_STATUS_DOWNLOADED
from core.downloaders.blackhole import BlackHole
from core.downloaders.jdownloader import JDownloader
from core.providers import get_providers
from core.repositories.downloaders import DownloaderRepository
from core.repositories.providers import ProviderRepository
from core.repositories.episodes import EpisodeRepository

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
    
    def __init__(self):
        self.downloaders = get_downloaders()
        self.providers = get_providers()
    
    def download(self, episode_id):
        # TODO Use priority for downloader order
        success = False
        episode_urls = self.episode_repository \
            .get_active_episode_urls(episode_id)
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