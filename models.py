from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


user_projects = Table(
    'user_projects', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

issue_labels = Table(
    'issue_labels', Base.metadata,
    Column('issues_id', Integer, ForeignKey('issues.id')),
    Column('labels_id', Integer, ForeignKey('labels.id'))
)


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email_id = Column(String)
    github_access_token = Column(String)

    projects = relationship('Projects', cascade='all, delete-orphan', single_parent=True,
                            secondary=user_projects, backref='users')


class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'))

    repositories = relationship("Repository", cascade='all, delete-orphan', backref='projects')
    labels = relationship("Labels", cascade='all, delete-orphan', backref='projects')


class Repository(Base):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    github_repo_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'))

    issues = relationship("Issues", cascade='all, delete-orphan')


class Issues(Base):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(String)
    repository = Column(Integer, ForeignKey('repository.id'))

    labels = relationship('Labels', cascade='all, delete-orphan', single_parent=True,
                          secondary=issue_labels, backref='issues')


class Labels(Base):
    __tablename__ = 'labels'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)
    order = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'))
