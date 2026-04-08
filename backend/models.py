from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from .database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    geom = Column(Geometry('POINT'))
