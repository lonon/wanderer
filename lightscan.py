from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship


from base import Base

class Lightscan(Base):

    __tablename__ = 'lightscan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    md5_hash = Column(String(40), ForeignKey('hosts.md5_hash'),nullable=False,unique=True)
    result = Column(Text(512))
    recent_change = Column(Boolean(), default=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    hosts = relationship("Hosts", backref="lightscan")


    def __init__(self, md5_hash,result,recent_change=False):
        self.md5_hash = md5_hash
        self.result = result
        self.recent_change = recent_change
