import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
