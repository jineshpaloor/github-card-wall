from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

user_projects = Table('user_projects', Base.metadata,
                      Column('user_id', Integer, ForeignKey('users.id')),
                      Column('project_id', Integer, ForeignKey('projects.id')))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(String(200))
    projects = relationship('Project', secondary=user_projects, backref='users')

    def __init__(self, name, access_token):
        self.username = name
        self.github_access_token = access_token


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    author_id = Column(Integer, ForeignKey('users.id'))
    repositories = relationship("Repository", backref='projects')

    def __init__(self, name, author):
        self.name = name
        self.author_id = author


class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    github_repo_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'))

    def __init__(self, name, repo_id, project_id):
        self.name = name
        self.github_repo_id = repo_id
        self.project_id = project_id


class Label(Base):
    __tablename__ = 'labels'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    project_id = Column(Integer, ForeignKey('projects.id'))

    def __init__(self, name, prj_id):
        self.name = name
        self.project_id = prj_id
