from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, \
    Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from core.db import engine

SHOW_STATUS_CONTINUING = 0
SHOW_STATUS_ENDED = 1
EPISODE_STATUS_WANTED = 0
EPISODE_STATUS_IGNORED = 1 
EPISODE_STATUS_SNATCHED = 2
EPISODE_STATUS_DOWNLOADED = 3
ERROR = -1

Base = declarative_base()

class Show(Base):
    __tablename__ = 'show'
    id = Column(Integer, primary_key = True)
    name = Column(String(256), index = True)
    status = Column(SmallInteger, default = SHOW_STATUS_CONTINUING)
    created = Column(DateTime)
    wanted = Column(Boolean, default = False)
    completed = Column(Boolean, default = False)
    episodes = relationship('Episode', backref = 'show', lazy = 'dynamic')
    urls = relationship('ShowUrl', backref = 'show', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Show %r>' % (self.name)
        
class ShowUrl(Base):
    __tablename__ = 'showurl'
    id = Column(Integer, primary_key = True)
    url = Column(String(2000))
    show_id = Column(Integer, ForeignKey('show.id'))
    provider = Column(String(256))
    
    def __repr__(self):
        return '<ShowUrl %r>' % (self.url)

class Episode(Base):
    __tablename__ = 'episode'
    id = Column(Integer, primary_key = True)
    number = Column(Integer)
    number_postfix = Column(String(10))
    airdate = Column(DateTime)
    show_id = Column(Integer, ForeignKey('show.id'))
    status = Column(SmallInteger, default = EPISODE_STATUS_IGNORED)
    urls = relationship('EpisodeUrl', backref='episode', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Episode %r>' % (self.number)
    
class EpisodeUrl(Base):
    __tablename__ = 'episodeurl'
    id = Column(Integer, primary_key = True)
    name = Column(String(256))
    url = Column(String(2000))
    episode_id = Column(Integer, ForeignKey('episode.id'))
    provider = Column(String(256))
    
    def __repr__(self):
        return '<EpisodeUrl %r>' % (self.name)

Base.metadata.create_all(engine)