from core.db import Session
from core.entities.models import Downloader

class DownloaderRepository(object):
    def get_downloaders(self):
        session = Session()
        downloaders = session.query(Downloader).all()
        
        return downloaders
        
    def save_downloader(self, downloader):
        session = Session.object_session(downloader)
        if session == None:
            session = Session()
        session.add(downloader)
        session.commit()
        session.refresh(downloader)