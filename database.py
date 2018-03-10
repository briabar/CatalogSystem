from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catagories(Base):

    __tablename__ = 'catagories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        '''returns object data in easily serializable format'''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class Items(Base):

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    time = Column(DateTime, nullable=False)
    cat_id = Column(Integer, ForeignKey('catagories.id'))
    cat_name = Column(String(80), nullable=False)
    catagories = relationship(Catagories)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        '''returns object data in easily serializable format'''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cat_name': self.cat_name,
            'time': self.time,
            'cat_id': self.cat_id,
        }


engine = create_engine('postgresql:///catalogdb.db')
Base.metadata.create_all(engine)
