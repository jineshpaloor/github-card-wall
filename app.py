import os
import json
from collections import defaultdict
from flask import Flask, request, g, session, redirect, url_for
from flask import jsonify
from flask import render_template
from flask.ext.github import GitHub as AuthGithub
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from local_settings import DATABASE_URI, SECRET_KEY, DEBUG, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from models import Labels, Repositories, Projects, Users, Base, Issues
from forms import ProjectForm, ProjectLabelsForm, ProjectIssueForm, ProjectMemberForm
from decorator import login_required

from datetime import datetime
import logging
from github_api import get_user_login_name, get_repo_list, get_label_list, \
    get_issue_dict, change_issue_label, create_new_issue, get_users_list

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# setup sqlalchemy
engine = create_engine(os.environ['DATABASE_URL'], isolation_level="READ UNCOMMITTED")
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

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
        g.user = Users.query.get(session['user_id'])


# gets called after every HTTP request has been serviced by the server
@app.after_request
def after_request(response):
    db_session.remove()
    return response


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
    next_url = request.args.get('next') or url_for('projects')
    if access_token is None:
        return redirect(next_url)

    user_name = get_user_login_name(access_token)
    user = Users.query.filter_by(username=user_name).first()
    if user is None:
        user = Users(username=user_name, github_access_token=access_token)
    else:
        user.github_access_token = access_token

    db_session.add(user)
    db_session.commit()

    session['user_id'] = user.id
    return redirect('/projects')


# the scope parameter is important as it decides
# what one can do with Github object
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/github-login')
def github_login():
    return github.authorize(scope='repo')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    g.user = None
    return redirect('/login')


@app.route('/new-project', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm(request.form)
    if request.method == 'POST':
        form.repositories.choices = get_repo_list(g.user)
        if form.validate():
            project = Projects(name=form.name.data, author_id=g.user.id)
            db_session.add(project)
            db_session.commit()
            repo_name_list = []
            for repo in form.repositories.data:
                repo_id, repo_name = repo.split('*')
                repo_name_list.append(repo_name)
                repository = Repositories(
                    name=repo_name, github_repo_id=repo_id, 
                    project_id=project.id)
                db_session.add(repository)
            db_session.commit()
            return redirect('/project/{0}/labels'.format(project.id))

    # this is for GET request
    form.repositories.choices = get_repo_list(g.user)
    return render_template(
        "new_project.html", form=form, view_url=url_for('new_project'))


@app.route('/')
@app.route('/projects')
@login_required
def projects():
    projects = Projects.query.filter_by(author_id=g.user.id)
    return render_template("projects.html", project_list=projects)


@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Projects.query.get(int(project_id))
    if request.method == 'GET':
        form = ProjectForm(obj=project)
        form.repositories.choices = get_repo_list(g.user)
        form.repositories.data = ['{0}*{1}'.format(repo.github_repo_id, repo.name)
                                  for repo in project.repositories]

        return render_template('new_project.html', form=form,
                               view_url=url_for('edit_project', project_id=project_id))
    else:
        # for POST method type
        form = ProjectForm(request.form)

        new_repo_id_name_dict = dict([repo.split('*') for repo in form.repositories.data])
        new_repos = new_repo_id_name_dict.values()


        project_repos = [repo.name for repo in project.repositories]

        obsolete_repos = set(project_repos) - set(new_repos)
        repos_to_be_added = set(new_repos) - set(project_repos)

        # remove obsolete repos
        for repo_name in obsolete_repos:
            repo_objects = Repositories.query.filter_by(name=repo_name, project_id=project.id)
            for repo in repo_objects:
                db_session.delete(repo)
        db_session.commit()

        # create new repos
        for repo_name in repos_to_be_added:
            repo_id = [id for (id, name) in new_repo_id_name_dict.items() if name == repo_name]
            repo_object = Repositories(name=repo_name, github_repo_id=repo_id[0], project_id=project.id)
            db_session.add(repo_object)
        db_session.commit()

        return render_template("select_labels.html", project=project,
                               label_list=get_label_list(g.user, new_repos))


@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Projects.query.get(int(project_id))
    db_session.delete(project)
    db_session.commit()

    return redirect('/projects')


@app.route('/project/<int:project_id>/labels', methods=['GET', 'POST'])
@login_required
def add_labels(project_id):
    project = Projects.query.get(int(project_id))
    if request.method == 'GET':
        labels = get_label_list(g.user, [repo.name for repo in project.repositories])
        labels_form = ProjectLabelsForm()
        labels_form.labels.choices = [(l, l) for l in labels]
        labels_form.labels.data = [l.name for l in project.labels]
        return render_template("select_labels.html", project=project, form=labels_form)
    else:
        #project = Projects.query.get(project_id)
        # if this is editing an existing project, delete existing labels
        for lbl in project.labels:
            db_session.delete(lbl)

        # save selected labels
        for i, lbl in enumerate(request.form.getlist('labels')):
            label = Labels(name=lbl, project_id=project.id, order=i+1)
            db_session.add(label)
        db_session.commit()
        return redirect(url_for('select_members', project_id=project_id))


@app.route('/project/<int:project_id>/select-members', methods=['GET', 'POST'])
@login_required
def select_members(project_id):
    project = Projects.query.get(int(project_id))
    if request.method == 'GET':
        repo_name_list = [repo.name for repo in project.repositories]
        collaborators = get_users_list(g.user, repo_name_list)

        members_form = ProjectMemberForm()
        members_form.members.choices = [(member.id, member.login) for member in collaborators]
        #members_form.members.data = [member.login for member in project.members]

        return render_template("select_members.html", project=project, form=members_form)
    else:
        # TODO : save the selection
        return redirect(url_for('order_labels', project_id=project_id))


@app.route('/project/<int:project_id>/order-labels', methods=['GET'])
@login_required
def order_labels(project_id):
    project = Projects.query.get(int(project_id))
    # labels need to be shown as per order
    labels = Labels.query.filter_by(project_id=project_id).order_by('order')
    return render_template('order_labels.html', labels=labels, project=project)


@app.route('/project/<int:project_id>/update-labels', methods=['GET', 'POST'])
def update_labels_order(project_id):
    project = Projects.query.get(int(project_id))
    if request.method == 'GET':
        d = request.args.get('labels')
        d = dict(request.args)
        for label, index in d.items():
            Labels.query.filter_by(
                name=label, project_id=project_id
            ).update({'order': index[0]})

        db_session.commit()
    return jsonify({'success': True, 'message': 'Label order saved!'})


@app.route('/change_label', methods=['GET'])
def change_label():
    issue_id = request.args.get('issue_id')
    from_label = request.args.get('from_label')
    to_label = request.args.get('to_label')
    issue_number = request.args.get('issue_no')
    repo_name = request.args.get('repo')
    change_issue_label(g.user, from_label, to_label, repo_name, issue_number)

    return jsonify({'success' : True, 'issue_id' : issue_id})


def update_issues(issue_dict, project_id):
    repo_dict = {}
    for label, gh_issue_list in issue_dict.items():
        for gh_issue in gh_issue_list:
            # get the repository object for this issue
            repo = repo_dict.get(gh_issue.repository.id)
            if repo is None:
                repo = Repositories.query.filter_by(project_id=project_id, github_repo_id=gh_issue.repository.id).first()
                repo_dict.setdefault(gh_issue.repository.id, repo)
            # check whether DB Issue exists for the project with DB repo.id and github issue number
            # If not create one
            # Also, we have to save the labels associated with the issues.
            instance = Issues.query.filter_by(repository_id=repo.id, number=gh_issue.number).first()
            if not instance:
                db_issue = Issues(repository_id=repo.id, title=gh_issue.title, body=gh_issue.body, number=gh_issue.number)
                # update the issue labels
                # Get all the labels registered for the project
                project_labels = Labels.query.filter_by(project_id=project_id)
                label_names = [l.name for l in project_labels]
                for gh_lbl in gh_issue.labels:
                    if gh_lbl.name in label_names:
                        project_label = Labels.query.filter_by(project_id=project_id, name=gh_lbl.name).first()
                        db_issue.labels.append(project_label)
                db_session.add(db_issue)
        db_session.commit()
    return True


def get_project_issue_dict(project, DB=True):
    issue_dict = defaultdict(list)
    if DB:
        for repo in project.repositories:
            for issue in repo.issues:
                for label in issue.labels:
                    issue_dict[label.name].append(issue)
    else:
        repo_list = [repo.name for repo in project.repositories]
        labels = Labels.query.filter_by(project_id=project.id).order_by('order')
        issue_dict = get_issue_dict(g.user, repo_list, labels)
        #update_issues(issue_dict, project.id)
    return issue_dict


@app.route('/project/<int:project_id>', methods=['GET'])
@login_required
def show_project(project_id):
    project = Projects.query.get(int(project_id))

    form = ProjectIssueForm(request.form)
    form.repository.choices = [('{0}*{1}'.format(repo.id, repo.name), repo.name)
                               for repo in project.repositories]

    labels = Labels.query.filter_by(project_id=project_id).order_by('order')
    issue_dict = get_project_issue_dict(project, DB=False)

    return render_template('issues_list.html', project=project, label_list=labels,
                           issues_dict=issue_dict, form=form,
                           create_url=url_for('new_issue', project_id=project_id))


@app.route('/project/<int:project_id>/issue/new', methods=['GET','POST'])
def new_issue(project_id):
    form = ProjectIssueForm(request.args)
    repo_id, repo_name = form.repository.data.split('*')
    issue = create_new_issue(
        user=g.user, repo_name=repo_name, title=form.title.data, 
        body=form.body.data, label_name=form.label.data)
    label = Labels.query.filter_by(name=form.label.data).first()
    html = str(render_template('issue.html', issue=issue, label=label))
    return jsonify({'success' : True, 'html' : html})

if __name__ == '__main__':
    import os
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
