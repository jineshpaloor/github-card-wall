from github import Github
from collections import defaultdict
import urllib
import logging


def get_user_login_name(access_token):
    github = Github(login_or_token=access_token)
    return github.get_user().login


def get_project_list(user_id):
    pass

def get_a_repo(github_user, repo_name):
    f_list = filter(lambda r:r.name == repo_name, github_user.get_repos(type='all'))
    return f_list[0]

def get_repo_list(user):
    """ Get all github repositories of the user."""
    github = Github(login_or_token=user.github_access_token)
    git_user = github.get_user()
    return [('{0}*{1}'.format(repo.id, repo.name), repo.name) 
            for repo in git_user.get_repos(type='all')]


def get_label_list(user, repo_name_list):
    label_list = set()
    github = Github(login_or_token=user.github_access_token)
    git_user = github.get_user()

    for repo_name in repo_name_list:
        repo = get_a_repo(git_user, repo_name)
        for lbl in repo.get_labels():
            label_list.add(lbl.name)
        #repo = git_user.get_repos(user.username+'/'+repo_name)
        # lbl_list = [lbl for lbl in repo.get_labels()]
        # for lbl in lbl_list:
        #     label_list.add(lbl.name)
    return label_list


def get_issue_dict(user, repo_list, lbl_list):
    github = Github(login_or_token=user.github_access_token)
    git_user = github.get_user()
    label_names = [l.name for l in lbl_list]

    issues_dict = defaultdict(list)

    for repo_name in repo_list:
        repo = get_a_repo(git_user, repo_name)
        issue_list = repo.get_issues()
        for issue in issue_list:
            for lbl in issue.labels:
                if lbl.name in label_names:
                    issues_dict[lbl.name].append(issue)
    return issues_dict


def change_issue_label(user, lbl_from, lbl_to, repo_name, issue_number):
    github = Github(login_or_token=user.github_access_token)
    git_user = github.get_user()
    repo = get_a_repo(git_user, repo_name)

    issue = repo.get_issue(int(issue_number))

    # remove the from label
    issue.remove_from_labels(urllib.quote(lbl_from))

    # check if new label exists in the repository
    # get all labels from this repository
    labels = [label for label in repo.get_labels()]

    if any(filter(lambda l:l.name == lbl_to, labels)):
        # get the label object
        new_label = repo.get_label(lbl_to)
    else:
        # create the new label in repository
        new_label = repo.create_label(lbl_to, "00ff00")

    issue.add_to_labels(new_label)

    return new_label

# def get_repository(user, github, repo_name):
#     return github.get_repo(user.username + '/' + repo_name)
