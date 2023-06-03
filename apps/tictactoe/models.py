from sqlalchemy import Column, Date, Integer, String

from db import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)
    test = Column(String)
    test2 = Column(Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date
