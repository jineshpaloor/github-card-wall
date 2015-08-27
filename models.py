from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import PrimaryKeyConstraint

Base = declarative_base()


user_projects = Table(
    'user_projects', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    PrimaryKeyConstraint('user_id', 'project_id')
)

issue_labels = Table(
    'issue_labels', Base.metadata,
    Column('issue_id', Integer, ForeignKey('issues.id')),
    Column('label_id', Integer, ForeignKey('labels.id')),
    PrimaryKeyConstraint('issue_id', 'label_id')
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

    repositories = relationship("Repositories", cascade='all, delete-orphan', backref='projects')
    labels = relationship("Labels", cascade='all, delete-orphan', backref='projects')


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    github_repo_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    issues = relationship("Issues", cascade='all, delete-orphan', backref='repositories')


class Issues(Base):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(String)
    number = Column(Integer)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)

    labels = relationship('Labels', secondary=issue_labels, backref='issues')

    UniqueConstraint(number, repository_id)


class Labels(Base):
    __tablename__ = 'labels'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)
    order = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
