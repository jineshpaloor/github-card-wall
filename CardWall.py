from github import Github
from local_settings import GITHUB_PROFILE, REPOSITORIES, LABELS
from collections import defaultdict

__author__ = 'rbansal'


class CW_Repository(object):
    def __init__(self, git_hub, name):
        self.repo = git_hub.get_repo(name)
        self.label_list = []
        self.issue_list = []

    def get_issues(self, lbl_names):
        # print "# of label names = %d" % len(lbl_names)

        # get all label objects for the names provided
        self.label_list = [self.repo.get_label(name) for name in lbl_names]

        # get all issues for these labels
        self.issue_list = [CW_Issue(issue)
                           for label in self.label_list
                           for issue in self.repo.get_issues(labels=[label])]

        # print "# of issues = %d" % len(self.issue_list)

        # return the issue list back
        return self.issue_list

    def has_issue(self, issue):
        return any(filter(lambda iss: iss == issue, self.issue_list))

    def move_issue(self, issue, lbl, new_lbl):
        if self.has_issue(issue):
            # change labels
            return issue.change_label(lbl, new_lbl)
        else:
            return None

    def __cmp__(self, other):
        return self.repo.name == other.repo.name


class CW_Issue(object):
    def __init__(self, iss):
        self.issue = iss
        self.label_list = []
        self.get_labels()

    def get_labels(self):
        self.label_list = [label for label in self.issue.get_labels()]

    def get_title(self):
        return self.issue.title

    def has_label(self, label):
        return any(filter(lambda l:l.name == label, self.label_list))

    def change_label(self, from_lbl, to_lbl):
        # remove the old label
        self.issue.remove_from_labels(self.issue.repository.get_label(from_lbl))

        # add the new label
        # check if new label exists in the repository, o/w create it
        to_lbl_obj = self.issue.repository.get_label(to_lbl)
        if to_lbl_obj is None:
            to_lbl_obj = self.issue.repository.create_label(to_lbl, "00ff00")

        self.issue.add_to_labels(to_lbl_obj)

        # refresh the label list
        self.get_labels()

        return self

    def __cmp__(self, other):
        return self.issue == other.issue

    def __str__(self):
        return "%s" % self.issue.title


class ProjectCardWall(object):
    def __init__(self, name):
        self.name = name
        self.issues_dict = defaultdict(list)

        # initialize the Github instance
        self.git_hub = Github(GITHUB_PROFILE.get('user_name'), GITHUB_PROFILE.get('password'))

        # read all the repositories for this user
        self.repo_list = [CW_Repository(self.git_hub, name) for name in REPOSITORIES]
        # print "# of repositories = %d" % len(self.repo_list)

        # get all the label objects from Github
        # self.label_list = list(set([label for label_gen in label_gen_list for label in label_gen]))

        self.label_order_dict = {
            'help wanted': 1, 'wontfix': 5, 'question': 2, 
            'bug': 4, 'enhancement': 3}
        self.label_order = ['help wanted', 'question', 'enhancement',  'bug', 'wontfix']

    def get_issue_list(self):
        # send API request and get issues with custom labels
        # read all the issues for each of the repositories
        for repo in self.repo_list:
            issue_list = repo.get_issues(self.label_order)

            for label in self.label_order:
                # print "label is %s" % label
                self.issues_dict[label].extend(
                    issue for issue in issue_list
                    if issue.has_label(label))

        return self.issues_dict

    def find_issue(self, issue_id, label):
        for item in self.issues_dict.get(label):
            if item.issue.id == issue_id:
                return item
        return None
