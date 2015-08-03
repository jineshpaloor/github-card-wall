from github import Github
from local_settings import GITHUB_PROFILE, REPOSITORIES, LABELS
from flask import Flask, jsonify, request
from flask import render_template
from CardWall import ProjectCardWall

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/', methods=['GET'])
def index():
    project = ProjectCardWall("Sahaj")
    issues_dict = project.get_issue_list()
    return render_template(
        "index.html", issues_dict=issues_dict, 
        label_order_list=project.label_order)

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/issue/<int:issue_id>')
def show_issue(issue_id):
    # show the post with the given id, the id is an integer
    return 'Issue %d' % issue_id 

@app.route('/change_label')
def change_label():
    from_label = request.args.get('from_label')
    to_label = request.args.get('to_label')
    repo_name = "rohiban/" + request.args.get('repo')
    #repo_name = "rohiban/bagNBall"
    issue_id = request.args.get('issue_id').split('-')[1]

    issue = None
    success = False

    # crude of doing. This must be replaced
    git_hub = Github(GITHUB_PROFILE.get('user_name'), GITHUB_PROFILE.get('password'))
    repo = git_hub.get_repo(repo_name)
    issues = repo.get_issues()
    for issue in issues:
        if int(issue.id) == int(issue_id):
            issue = issue
            break

    if issue:
        frm_lbl = issue.repository.get_label(from_label)
        print 'form label is ', frm_lbl 
        issue.remove_from_labels(frm_lbl)

        to_lbl = issue.repository.get_label(to_label)
        if to_lbl is None:
            to_lbl = issue.repository.create_label(to_label, "00ff00")
        issue.add_to_labels(to_lbl)
        success = True
    return jsonify(result=success)

if __name__ == '__main__':
    app.run(debug=True)
