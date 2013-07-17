import logging
from core import container
from core.providers.torrent.hdzone import HdZone as HdZoneTorrent
from core.providers.directdl.hdzone import HdZone as HdZoneDirectdl

log = logging.getLogger(__name__)

container.providers = None

def get_providers():
    if container.providers == None:
        _load_providers()
    return container.providers

def _load_providers():
    log.info('Loading providers...')
    # TODO load provider modules
    loaded_providers = [ HdZoneDirectdl(), HdZoneTorrent()]
    
    container.providers = loaded_providers
    log.info('Finished loading providers...')