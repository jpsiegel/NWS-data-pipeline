from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.station import Station

class WeatherObservation(Base):
    """Stores weather readings from an NWS station"""

    __tablename__ = "weather_observations"
    
    # Attributes
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    
    # Values
    temperature = Column(Float, nullable=True) # Celsius
    wind_speed = Column(Float, nullable=True) # km/h
    wind_direction = Column(Float, nullable=True) # angular degree
    humidity = Column(Float, nullable=True) # %
    pressure = Column(Float, nullable=True) # Pa
    dewpoint = Column(Float, nullable=True) # Celsius
    visibility = Column(Float, nullable=True) # meters   

    # Relationships
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    station = relationship("Station", back_populates="observations")

    # Constraints
    __table_args__ = (
        UniqueConstraint('station_id', 'timestamp', name='unique_station_timestamp'),
        CheckConstraint("temperature IS NULL OR temperature >= -273.15", name="temperature_above_absolute_zero"),
        CheckConstraint("wind_direction IS NULL OR wind_direction BETWEEN 0 AND 360", name="valid_wind_direction"),
        CheckConstraint("humidity IS NULL OR humidity BETWEEN 0 AND 120", name="valid_humidity"),
        CheckConstraint("visibility IS NULL OR visibility >= 0", name="positive_visibility"),
    )

