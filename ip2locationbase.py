#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#MAKE CERTAIN THAT THAT PIECE IS REMOVED AS SOON AS CONVENIENT!!!
ip2locationengine = create_engine('mariadb+mariadbconnector://lui:lw4nd4@localhost/ip2location')
ip2locationSession = sessionmaker(bind=ip2locationengine)

ip2locationBase = declarative_base()
