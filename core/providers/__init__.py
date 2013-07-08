from core import container
from core.entities.models import Provider
from core.providers.torrent.hdzone import HdZone as HdZoneTorrent
from core.providers.directdl.hdzone import HdZone as HdZoneDirectdl
from core.repositories.providers import ProviderRepository

container.providers = None

def get_providers():
    if container.providers == None:
        print 'Loading providers...'
        _load_providers()
    print 'Finished loading providers...'
    return container.providers

def _load_providers():
    # TODO load provider modules
    loaded_providers = [ HdZoneDirectdl(), HdZoneTorrent()]
    
    _sync_providers_in_db(loaded_providers)
    container.providers = loaded_providers
    
def _sync_providers_in_db(loaded_providers):
    provider_repository = ProviderRepository()
    providers_from_db = _get_providers_from_db()
            
    for loader_provider in loaded_providers:
        if loader_provider.name in providers_from_db:
            provider = providers_from_db[loader_provider.name]
        else:
            # Insert provider to db
            # TODO Set default active state to False
            provider = Provider(name = loader_provider.name, 
                active = True)
            provider_repository.save_provider(provider)
        loader_provider.active = provider.active
        loader_provider.id = provider.id

def _get_providers_from_db():
    provider_repository = ProviderRepository()
    providers_from_db = provider_repository.get_providers()
    db_providers = {}
    for provider in providers_from_db:
        db_providers[provider.name] = provider
    return db_providers