from datetime import datetime, timedelta
from core.db import Session
from core.entities.models import Show, SHOW_STATUS_CONTINUING

class ShowRepository(object):
    def get_shows(self, status = None, order_by = [], limit = None, \
        wanted = None):
        session = Session()
        shows = session.query(Show)
        
        if not status == None:
            shows = shows.filter_by(status = status)
            
        if wanted:
            shows = shows.filter_by(wanted = wanted)
        
        for order in order_by:
            shows = shows.order_by(order)
        
        if not limit == None:
            shows = shows.limit(limit)
            
        return shows.all()
        
    def get_all_shows(self):
        return self.get_shows()
        
    def get_continuing_shows(self):
        return self.get_shows(status = SHOW_STATUS_CONTINUING, 
            order_by = [Show.created.desc()], limit =5)
            
    def get_wanted_shows(self):
        return self.get_shows(wanted = True, order_by = \
            [Show.status, Show.created.desc()])
            
    def get_manageable_shows(self):
        session = Session()
        manageable_shows = session.query(Show).filter(Show.created > (datetime.utcnow() - \
            timedelta(days=90))).order_by(Show.status)\
            .order_by(Show.created.desc()).all()
        
        return manageable_shows
            
    def get_show(self, show_id):
        session = Session()
        show = session.query(Show).filter_by(id = show_id).first()
        
        return show
        
    def save_show(self, show):
        session = Session.object_session(show)
        if session == None:
            session = Session()
        session.add(show)
        session.commit()
        session.refresh(show)