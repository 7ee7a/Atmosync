from sqlalchemy import Column, Integer, String, Float, DateTime
from geoalchemy2 import Geometry
from .database import Base
import datetime

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    geom = Column(Geometry('POINT'))

class AtmosphericGrid(Base):
    __tablename__ = "atmospheric_grids"

    id = Column(Integer, primary_key=True, index=True)
    pollutant = Column(String, index=True) # e.g., 'PM2.5', 'NO2'
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    geom = Column(Geometry('POLYGON', srid=4326))

class GroundStation(Base):
    __tablename__ = "ground_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, index=True)
    pollutant = Column(String, index=True)
    latest_value = Column(Float)
    last_updated = Column(DateTime)
    geom = Column(Geometry('POINT', srid=4326))
