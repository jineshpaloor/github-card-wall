from flask import Flask
from flask import render_template
from card_wall import ProjectCardWall

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    p = ProjectCardWall("Sahaj")
    p.set_repo_list()
    p.build_issue_list()
    issues_dict = p.get_sorted_issues()
    return render_template("index.html", issues_dict=issues_dict)

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/issue/<int:issue_id>')
def show_issue(issue_id):
    # show the post with the given id, the id is an integer
    return 'Issue %d' % issue_id 


if __name__ == '__main__':
    app.run(debug=True)
