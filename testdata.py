from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database import Catagories, Base, Items

engine = create_engine('sqlite:///catalogdb.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Menu for UrbanBurger
catagory1 = Catagories(name="swimming")

session.add(catagory1)
session.commit()

item1 = Items(name="snorkle", description="for breathing.", cat_name=catagory1.name, time=datetime.datetime.now() ,catagories=catagory1)

session.add(item1)
session.commit()

# Menu for UrbanBurger

item2 = Items(name="flippers", description="For fast swimming.", cat_name=catagory1.name, time=datetime.datetime.now() ,catagories=catagory1)

session.add(item2)
session.commit()

# Menu for UrbanBurger
catagory2 = Catagories(name="weapons")

session.add(catagory2)
session.commit()

item3 = Items(name="gun", description="For shotting and killing.",cat_name=catagory2.name, time=datetime.datetime.now() ,catagories=catagory2)

session.add(item3)
session.commit()

# Menu for UrbanBurger

item4 = Items(name="mace", description="for the beatings.",cat_name=catagory2.name, time=datetime.datetime.now() ,catagories=catagory2)

session.add(item4)
session.commit()

# Menu for UrbanBurger

item5 = Items(name="burkini", description="swim suit that covers entire body.",cat_name=catagory1.name, time=datetime.datetime.now() ,catagories=catagory1)

session.add(item5)
session.commit()

# Menu for UrbanBurger

item6 = Items(name="scuba tank", description="holds air while breathing underwater.",cat_name=catagory1.name, time=datetime.datetime.now() ,catagories=catagory1)

session.add(item1)
session.commit()

print "added menu items!"
