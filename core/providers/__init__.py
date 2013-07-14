from core import container
from core.providers.torrent.hdzone import HdZone as HdZoneTorrent
from core.providers.directdl.hdzone import HdZone as HdZoneDirectdl

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
    
    container.providers = loaded_providers