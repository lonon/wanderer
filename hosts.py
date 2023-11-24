#!/usr/bin env python

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from base import Base

class Hosts(Base):
    __tablename__ = 'hosts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(30), nullable=False,unique=True)
    md5_hash = Column(String(40), nullable=False,unique=True)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    reliable = Column(Boolean(), default=False)

    def __init__(self, ip, md5_hash, reliable=False):
        self.ip = ip
        self.md5_hash = md5_hash
        self.reliable = reliable
