from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    
    # Attributes
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    station = relationship("Station", back_populates="observations")

