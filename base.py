#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#MAKE CERTAIN THAT THIS PIECE IS REMOVED AS SOON AS CONVENIENT!!!
engine = create_engine('mariadb+mariadbconnector://lui:lw4nd4@localhost/nefario') # <------------IYKYK
Session = sessionmaker(bind=engine)


Base = declarative_base()
