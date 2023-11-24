#!/usr/bin env python

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from sqlalchemy import Numeric, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship

from ip2locationbase import ip2locationBase

class IP2Location(ip2locationBase):

    __tablename__ = 'ip2location_db11'
    ip_from = Column(Integer(), primary_key=True)
    ip_to = Column(Integer())
    country_code = Column(String(16))
    country_name = Column(String(128))
    region_name = Column(String(128))
    latitude = Column(Float(64))
    longitude = Column(Float(64))
    zip_code = Column(String(30))
    time_zone = Column(String(10))

