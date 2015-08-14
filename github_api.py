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
    return [(repo.id, repo.name) for repo in github.search_repositories(query="user:"+user.username)]


# def get_repo_id(user, repo_name):
#     github = Github(login_or_token=user.github_access_token)
#     repo = github.get_repo(user.username+'/'+repo_name)
#     return repo.id

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
            # logging.info(label_name)

            for label in labels:
                if label.name == label_name:
                    issue_list = [issue for issue in repo.get_issues(labels=[label])]
                    #issues_dict[label_name] = issue_list
                    for issue in issue_list:
                        issues_dict[label_name].append(issue)
                        #issues_dict[label_name].append(myissue(issue.id, issue.title, issue.body, issue.repository.name))
    logging.info(issues_dict)
    return issues_dict

def change_issue_label(user, lbl_from, lbl_to, repo_name, issue_id):
    github = Github(login_or_token=user.github_access_token)
    repo = get_repository(user, github, repo_name)

    #logging.info('from label -----'+lbl_from)

    issue = repo.get_issue(int(issue_id))

    # remove the from label
    label = repo.get_label(lbl_from)
    logging.info('################## from label -----'+label.name)

    issue.remove_from_labels(str(lbl_from))

    logging.info('after removing from '+str(lbl_from))

    # check if new label exists in the repository
    # get all labels from this repository
    labels = [label for label in repo.get_labels()]

    if any(filter(lambda l:l.name == lbl_to, labels)):
        logging.info('if clause ------')
        logging.info(lbl_to)
        # get the label object
        new_label = repo.get_label(lbl_to)
    else:
        # create the new label in repository
        new_label = repo.create_label(lbl_to, "00ff00")

    issue.add_to_labels(new_label)
    logging.info('after adding to '+lbl_to)

    return new_label

def get_repository(user, github, repo_name):
    return github.get_repo(user.username + '/' + repo_name)


class myissue(object):
    def __init__(self, id, title, body, repo_name):
        self.id = id
        self.title = title
        self.body = body
        self.repo_name = repo_name

    def __cmp__(self, other):
        return self.id.__cmp__(other.id)