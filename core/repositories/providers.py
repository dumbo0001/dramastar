from core.db import Session
from core.entities.models import Provider

class ProviderRepository(object):
    def get_providers(self):
        session = Session()
        providers = session.query(Provider).all()
        
        return providers
    
    def get_provider(self, provider_id):
        session = Session()
        provider= session.query(Provider).filter_by(id = provider_id).first()
        
        return provider       
        
    def save_provider(self, provider):
        session = Session.object_session(provider)
        if session == None:
            session = Session()
        session.add(provider)
        session.commit()
        session.refresh(provider)
        
    def get_active_providers_by_episode(self, episode_id):
        session = Sesion()
        providers = session.query(Provider).filter_by(active = True) \
            .order_by(Provider.priority).join(EpisodeUrl) \
            .filter_by(episode_id = episode_id.id)
            
        return providers