from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI
    
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)