from flask import Flask, request, g, session, redirect, url_for
from flask import render_template_string
from flask import render_template
from flask.ext.github import GitHub as AuthGithub

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from local_settings import DATABASE_URI, SECRET_KEY, DEBUG, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from models import Repository, Project, User, Base

import logging
from github_api import get_user_login_name, get_repo_list

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.query = db_session.query_property()

logging.basicConfig(filename='CardWallApp.log', level=logging.INFO)


def init_db():
    Base.metadata.create_all(bind=engine)

# setup github-flask authentication instance
github = AuthGithub(app)

# gets called before every HTTP request is made
@app.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


# gets called after every HTTP request has been serviced by the server
@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/')
def index():
    return render_template("index.html")


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        logging.info("=== inside if clause ====")
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(get_user_login_name(access_token), access_token)
        db_session.add(user)
        db_session.commit()

    session['user_id'] = user.id
    return redirect('/projects')


@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize()
    else:
        return 'Already logged in'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    user = g.user
    if user is not None:
        return user.username


@app.route('/projects')
def projects():
    # projects = ['ekStep', 'Pratham Books', 'mUzima']
    projects = Project.query.filter_by(author_id=g.user.id)
    return render_template("projects.html", project_list=projects)


@app.route('/new_project')
def new_project():
    #project = Project(g.user.username, g.user.id)
    #db_session.add(project)
    #db_session.commit()
    return render_template("new_project.html", repo_dict=get_repo_list(g.user))

@app.route('/create_project', methods=['POST'])
def create_project():
    # pdb.set_trace()

    project = Project(request.form['project_name'], g.user.id)
    db_session.add(project)
    db_session.commit()

    #logging.info('-' * 20)
    #logging.info(len(request.form['repository[]']), request.form['repository'].__dict__)
    # repo_list = request.form['repository']

    for repo in repo_list:
        repo = Repository(repo, 456, project.id)
        db_session.add(repo)
    db_session.commit()
    return redirect('/projects')
    # return render_template("select_repos.html",
    #                        project_name=request.form['project_name'],
    #                        repo_dict=get_repo_list(g.user))

@app.route('/add_repos', methods=['POST'])
def add_repos():
    # for repo in request.form['repo_list']:
    #     if repo.get['selection'] == 'yes':
    #         Repository(repo.get['name'], repo.get['git_id'])
    project = Project(request.form['project_name'], g.user.id)
    repo = Repository(request.form['repository'], 123)
    db_session.add(project, repo)
    db_session.commit()
    return redirect('/projects')

if __name__ == '__main__':
    import os
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
