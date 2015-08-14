from github import Github
from collections import defaultdict
import logging


def get_user_login_name(access_token):
    github = Github(login_or_token=access_token)
    return github.get_user().login


def get_project_list(user_id):
    pass


def get_repo_list(user):
    github = Github(login_or_token=user.github_access_token)
    user = github.get_user()
    return [(repo.id, repo.name) for repo in user.get_repos(type='all')]
    #return [(repo.id, repo.name) for repo in github.search_repositories(query="user:"+user.username)]


def get_label_list(user, repo_name_list):
    label_list = set()
    github = Github(login_or_token=user.github_access_token)

    for repo_name in repo_name_list:
        repo = github.get_repo(user.username+'/'+repo_name)
        lbl_list = [lbl for lbl in repo.get_labels()]
        for lbl in lbl_list:
            label_list.add(lbl.name)
    return label_list


def get_issue_dict(user, repo_list, lbl_list):
    github = Github(login_or_token=user.github_access_token)
    issues_dict = defaultdict(list)

    for repo_name in repo_list:
        repo = get_repository(user, github,repo_name)
        labels = [label for label in repo.get_labels()]

        for label_name in lbl_list:
            for label in labels:
                if label.name == label_name:
                    issue_list = [issue for issue in repo.get_issues(labels=[label])]
                    for issue in issue_list:
                        issues_dict[label_name].append(issue)
    #logging.info(issues_dict)
    return issues_dict

def change_issue_label(user, lbl_from, lbl_to, repo_name, issue_id):
    github = Github(login_or_token=user.github_access_token)
    repo = get_repository(user, github, repo_name)

    issue = repo.get_issue(int(issue_id))

    # remove the from label
    issue.remove_from_labels(str(lbl_from))

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

def get_repository(user, github, repo_name):
    return github.get_repo(user.username + '/' + repo_name)
