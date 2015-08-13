from github import Github


def get_user_login_name(access_token):
    github = Github(login_or_token=access_token)
    return github.get_user().login


def get_project_list(user_id):
    pass


def get_repo_list(user):
    repo_dict = {}
    github = Github(login_or_token=user.github_access_token)
    repo_list = [repo.name for repo in github.search_repositories(query="user:"+user.username)]
    # for repo in repo_list:
    #     repo_dict[repo.name] = {'id': repo.id, 'selection':'no'}

    return repo_list

