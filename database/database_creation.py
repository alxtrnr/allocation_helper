# database_creation.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import sessionmaker

# Define the database engine
engine = create_engine('sqlite:///dev01.db')

# Define the base class for declarative models
Base = declarative_base()
converter = {'08:00': 0,
             '09:00': 1,
             '10:00': 2,
             '11:00': 3,
             '12:00': 4,
             '13:00': 5,
             '14:00': 6,
             '15:00': 7,
             '16:00': 8,
             '17:00': 9,
             '18:00': 10,
             '19:00': 11,
             '20:00': 0,
             '21:00': 1,
             '22:00': 2,
             '23:00': 3,
             '00:00': 4,
             '01:00': 5,
             '02:00': 6,
             '03:00': 7,
             '04:00': 8,
             '05:00': 9,
             '06:00': 10,
             '07:00': 11
             }


# Define the StaffTable class
class StaffTable(Base):
    __tablename__ = 'staff_table'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    role = Column(String(100))
    gender = Column(String(20))
    assigned = Column(Boolean, default=False)
    block = Column(Boolean, default=False)
    start_time = Column(Integer, default=0)
    end_time = Column(Integer, default=12)
    duration = Column(Integer)
    omit_time = Column(MutableList.as_mutable(PickleType), default=[])
    cherry_pick = Column(MutableList.as_mutable(PickleType), default=[])
    start = Column(String, default="shift start")
    end = Column(String, default="shift end")
    # omit = Column(MutableList.as_mutable(PickleType), default=['None'])
    omit = Column(String, default='')

    def __init__(self, name, role, gender, assigned, start_time, end_time, duration, omit_time=None, cherry_pick=None,
                 block=False):
        self.name = name
        self.role = role
        self.gender = gender
        self.assigned = assigned
        self.block = block
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.omit_time = omit_time or []
        self.cherry_pick = cherry_pick or []

        # Convert values for new columns
        self.start = converter.get(start_time)
        self.end = converter.get(end_time)
        self.omit_time_converted = [converter.get(t, 0) for t in omit_time] if omit_time else []

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Define the ObservationsTable class
class ObservationsTable(Base):
    __tablename__ = 'patient_table'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    observation_level = Column(String, default='0')
    obs_type = Column(String, default='ES')
    room_number = Column(String(100))
    gender_req = Column(String(20), default=None)
    omit_staff = Column(MutableList.as_mutable(PickleType), default=[])

    def __init__(self, name, observation_level, obs_type, room_number, gender_req=None, omit_staff=None):
        self.name = name
        self.observation_level = observation_level
        self.obs_type = obs_type
        self.room_number = room_number
        self.gender_req = gender_req
        self.omit_staff = omit_staff or []

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Create the tables in the database
Base.metadata.create_all(engine)
