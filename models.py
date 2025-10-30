from sqlalchemy import create_engine, Column, Integer, String, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()

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
    omit_time = Column(MutableList.as_mutable(PickleType))
    special_list = Column(MutableList.as_mutable(PickleType))
    special_string = Column(String, default='')
    start = Column(String, default='')
    end = Column(String, default='')
    omit = Column(String)
    def __init__(self, name, role, gender, assigned, start_time, end_time, duration, special_string='', omit_time=None, special_list=None, block=False):
        self.name = name
        self.role = role
        self.gender = gender
        self.assigned = assigned
        self.block = block
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.omit_time = omit_time or []
        self.special_list = special_list or []
        self.special_string = special_string
        self.start = start_time
        self.end = end_time
        self.omit_time_converted = self.omit_time
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PatientTable(Base):
    __tablename__ = 'patient_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    observation_level = Column(String, default='0')
    obs_type = Column(String, default=None)
    room_number = Column(String(100))
    gender_req = Column(String, default=None)
    omit_staff_selector = Column(String, default=None)
    omit_staff = Column(MutableList.as_mutable(PickleType), default=[''])
    def __init__(self, name, observation_level, obs_type, room_number, gender_req=None, omit_staff_selector=None, omit_staff=None):
        self.name = name
        self.observation_level = observation_level
        self.obs_type = obs_type
        self.room_number = room_number
        self.gender_req = gender_req
        self.omit_staff_selector = omit_staff_selector
        self.omit_staff = omit_staff or []
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def setup_engine(db_uri_or_path):
    """Create engine and tables for a given SQLite URI/path."""
    engine = create_engine(db_uri_or_path)
    Base.metadata.create_all(engine)
    return engine

def init_in_memory_db():
    """Helper for tests: sets up a fully in-memory SQLite DB, metadata creates tables, and returns Session, StaffTable, PatientTable."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session, StaffTable, PatientTable
