from sqlalchemy import ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

DATABASE_URL = "sqlite:///foodChain.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    founding_year = Column(Integer())

    # Relationships
    # Collection of all the freebies for the Company
    freebies = relationship('Freebie', back_populates='company')

    # Collection of all the devs who collected freebies from the company
    devs = relationship('Dev', secondary='freebies')

    def __init__(self, name, founding_year):
        self.name = name
        self.founding_year = founding_year

    # Give a freebie to a Dev
    def give_freebie(self, dev, item_name, value):
        freebie = Freebie(item_name=item_name, value=value, dev=dev, company=self)
        session.add(freebie)
        session.commit()

    # Class method to find the oldest company
    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()


class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer(), primary_key=True)
    name = Column(String())

    # Relationships
    # Collection of all the freebies that the Dev has collected
    freebies = relationship('Freebie', back_populates='dev')

    # Collection of all the companies that the Dev has collected freebies from
    companies = relationship('Company', secondary='freebies')

    def __init__(self, name):
        self.name = name

    # Check if the Dev has received a freebie with a specific item_name
    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    # Give away a freebie to another Dev
    def give_away(self, other_dev, freebie):
        if freebie.dev == self:
            freebie.dev = other_dev
            session.commit()


class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer(), primary_key=True)
    item_name = Column(String())
    value = Column(Integer())
    
    dev_id = Column(Integer(), ForeignKey('devs.id'))
    dev = relationship('Dev', backref=backref('freebies_given', cascade='all, delete-orphan'))
    
    company_id = Column(Integer(), ForeignKey('companies.id'))
    company = relationship('Company', backref=backref('freebies_given', cascade='all, delete-orphan'))

    def __init__(self, item_name, value, dev, company):
        self.item_name = item_name
        self.value = value
        self.dev = dev
        self.company = company

    # Relationship Attributes
    # Dev instance for this Freebie
    @property
    def dev(self):
        return self.dev

    # Company instance for this Freebie
    @property
    def company(self):
        return self.company

    # Print details of the Freebie
    def print_details(self):
        return f'{self.dev.name} owns a {self.item_name} from {self.company.name}'

