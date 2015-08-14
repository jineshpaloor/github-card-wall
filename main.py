from flask import Flask, request, g, session, redirect, url_for
from flask import render_template_string, jsonify
from flask import render_template
from flask.ext.github import GitHub as AuthGithub

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from local_settings import DATABASE_URI, SECRET_KEY, DEBUG, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from models import Label, Repository, Project, User, Base

import logging
from github_api import get_user_login_name, get_repo_list, get_label_list, get_issue_dict, change_issue_label

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


# is called by Github to access the token when it needs
@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


# is called by extension api to handover the token
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


# the scope parameter is important as it decides
# what one can do with Github object
@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(scope='repo')
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
    projects = Project.query.filter_by(author_id=g.user.id)
    return render_template("projects.html", project_list=projects)

@app.route('/new_project')
def new_project():
    return render_template("new_project.html", repo_list=get_repo_list(g.user))

@app.route('/create_project', methods=['POST'])
def create_project():
    project = Project(request.form['project_name'], g.user.id)
    db_session.add(project)
    db_session.commit()

    repo_name_list = []
    for repo in request.form.getlist('repository'):
        repo_id, repo_name=repo.split('*')
        repo_name_list.append(repo_name)
        repository = Repository(repo_name, repo_id, project.id)
        db_session.add(repository)
    db_session.commit()
    return render_template("select_labels.html", project_name=project.name,
                           label_list=get_label_list(g.user, repo_name_list))

@app.route('/add_labels', methods=['POST'])
def add_labels():
    project = Project.query.filter_by(name=request.form['project']).first()
    repo_list = []
    for repo in project.repositories:
        repo_list.append(repo.name)
    lbl_list = []
    for lbl in request.form.getlist('labels'):
        lbl_list.append(lbl)
        label = Label(lbl, project.id)
        db_session.add(label)
    db_session.commit()
    issue_dict = get_issue_dict(g.user, repo_list, lbl_list)
    return render_template('/issues_list.html', label_list=lbl_list, issues_dict=issue_dict)


@app.route('/change_label', methods=['GET'])
def change_label():
    from_label = request.args.get('from_label')
    to_label = request.args.get('to_label')
    issue_number = request.args.get('issue_id')
    repo_name = request.args.get('repo')
    change_issue_label(g.user, from_label, to_label, repo_name, issue_number)

    return jsonify({'success':True})

@app.route('/show_project', methods=['POST'])
def show_project():
    project_id = request.form.get('project-id')
    project = Project.query.get(int(project_id))
    lbl_list = [label.name for label in project.labels]
    repo_list = [repo.name for repo in project.repositories]
    issue_dict = get_issue_dict(g.user, repo_list, lbl_list)
    return render_template('/issues_list.html', project_name=project.name,
                           label_list=lbl_list, issues_dict=issue_dict)

if __name__ == '__main__':
    import os
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
