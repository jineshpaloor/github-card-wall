from github import Github


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
