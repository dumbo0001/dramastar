from datetime import datetime, timedelta
from core.db import Session
from core.entities.models import Episode, EPISODE_STATUS_WANTED, Show, \
    Provider, EpisodeUrl

class EpisodeRepository(object):
    def get_episodes(self, show = None, order_by = []):
        session = Session()
        episodes = session.query(Episode)
        
        if not show == None:
            episodes = episodes.filter_by(show_id = show.id)
        
        for order in order_by:
            episodes = episodes.order_by(order)
            
        return episodes.all()
        
    def get_show_episodes(self, show):
        return self.get_episodes(show = show, order_by = [Episode.number])
        
    def get_latest_episodes(self):
        session = Session()
        episodes = session.query(Episode)
        return episodes \
            .filter_by(status = EPISODE_STATUS_WANTED) \
            .filter(Episode.airdate > (datetime.utcnow() - timedelta(days=5))) \
            .join(Show).filter_by(wanted = True) \
            .order_by(Episode.airdate.desc()).all()
    
    def get_episode(self, episode_id):
        session = Session()
        episode = session.query(Episode).filter_by(id = episode_id).first()
        
        return episode
        
    def save_episode(self, episode):
        session = Session.object_session(episode)
        if session == None:
            session = Session()
        session.add(episode)
        session.commit()
        session.refresh(episode)
        
    def get_active_episode_urls(self, episode_id):
        session = Session()
        episode_urls = session.query(EpisodeUrl)\
            .filter_by(episode_id = episode_id).join(Provider).filter_by(active = True) \
            .order_by(Provider.priority).all()
            
        return episode_urls