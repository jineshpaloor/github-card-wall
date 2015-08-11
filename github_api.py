from github import Github

def get_user_login_name(access_token):
    github = Github(login_or_token=access_token)
    return github.get_user().login
