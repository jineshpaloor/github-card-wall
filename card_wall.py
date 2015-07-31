from github import Github
from local_settings import GITHUB_PROFILE, REPOSITORIES
from collections import defaultdict

__author__ = 'rbansal'


class ProjectCardWall(object):
    def __init__(self, name):
        self.name = name
        self.repo_list = []
        self.sorted_issues_dict = defaultdict(list)

        # initialize the Github instance
        self.git_hub = Github(
            GITHUB_PROFILE.get('user_name'), 
            GITHUB_PROFILE.get('password'))

    def set_repo_list(self):
        # read all the repositories for this user
        # self.repo_list = self.git_hub.get_repos()
        self.repo_list = [self.git_hub.get_repo(name) for name in REPOSITORIES]

    def build_issue_list(self):
        # send API request and get issues with custom labels
        # read all the issues for each of the repositories
        for repo in self.repo_list:
            issues = repo.get_issues()
            for issue in issues:
                for label in issue.labels:
                    self.sorted_issues_dict[label.name].append(issue)

    def get_sorted_issues(self):
        return self.sorted_issues_dict
