from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from core.config import configmanager
    
engine = create_engine(configmanager.get('databases', 'uri'), echo = False)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)