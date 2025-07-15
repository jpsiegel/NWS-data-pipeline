from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class Station(Base):
    __tablename__ = "stations"

    # Attributes
    id = Column(Integer, primary_key=True, index=True)
    nws_id = Column(String, unique=True, index=True) # id from National Weather Service
    name = Column(String, nullable=False)
    timezone = Column(String, nullable=True) # e.g. America/Santiago
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relationships
    observations = relationship("WeatherObservation", back_populates="station")

