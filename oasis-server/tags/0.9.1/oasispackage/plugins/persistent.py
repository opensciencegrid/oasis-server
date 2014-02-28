#!/usr/bin/env python 


import os

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import orm
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ConfigParser import SafeConfigParser


Base = declarative_base()
class Message(Base):
    '''
    
    '''
    

    __tablename__ = "Message"
    id = Column(Integer, primary_key=True)
    message = Column(String)

    def __eq__(self, x):
        
        if not self.message == x.message:
            return False
        return True


class PersistenceDB(object):
    '''
    
    class to handle the info in the DB
    '''
    

    def __init__(self, config, type):    

        self.config = config
        self.instance_type = type

        self._setup()

    def _setup(self):
        '''
        
        Create connection URI/DB string and setup DB if not existing. 
        '''
        
        
        self.dburi =""
        self.dbengine=self.config.get('persistence', 'persistence.dbengine')
        self.dburi += self.dbengine
        
        self.dbuser=self.config.get('persistence', 'persistence.dbuser')
        self.dbpassword=self.config.get('persistence', 'persistence.dbpassword')
        if self.dbuser and self.dbpassword:
            self.dburi += "%s:%s" % (self.dbuser, self.dbpassword)
        
        self.dbhost=self.config.get('persistence', 'persistence.dbhost')
        self.dbport=self.config.get('persistence', 'persistence.dbport')
        self.dbpath = os.path.expanduser(self.config.get('persistence', 'persistence.dbpath'))
        
        if self.dbhost and self.dbport and self.dbpath:
            self.dburi += "@%s:%s/%s" % ( self.dbhost, self.dbport, self.dbpath)
        elif self.dbpath:
            self.dburi += "/%s" % self.dbpath
        
        self.engine = create_engine(self.dburi)
        
        self.metadata = Base.metadata
        self.metadata.create_all(self.engine)

        # create the session
        _session = sessionmaker()
        _session.configure(bind=self.engine)
        self.session = _session()

        # query
        self.messages = self.session.query(self.instance_type).all()
        
    def getinstance(self, reference):
        #
        #  Note: maybe this can be done better 
        #        using filter_by() 
        #        instead of getting everything and 
        #        searching for the object we are interested in
        #
        instances = self.session.query(self.instance_type).all()
        for i in instances:
            if i == reference:
                return i
        return None

    def refresh(self):
        self.messages = self.session.query(self.instance_type).all()

    def save(self):
        self.session.flush()
        self.session.commit()
    

# ------ examples --------

#conf = SafeConfigParser()
#conf.readfp( open('/conf') )
#o = PersistenceDB(conf, Message)

#o.session.add(Message(message='msg1'))
#o.save()

#i = o.getinstance(Message(message = 'msg1'))
#o.session.delete(i)
#o.save()
