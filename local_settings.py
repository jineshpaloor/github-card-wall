import os
DATABASE_URI = 'sqlite:///cardwall.db'
#DATABASE_URI = "postgresql://localhost/cardwall"
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #os.urandom(32) #
DEBUG = True
LOCAL = False

# Set these values
if LOCAL:
    GITHUB_CLIENT_ID = '6996e3232399d753d554' 
    GITHUB_CLIENT_SECRET = 'e0ec5f6129617ec01fa50a393b154bc3c306f2a2' 
else:
    GITHUB_CLIENT_ID = '6e64c0848143de395527'
    GITHUB_CLIENT_SECRET = 'b03748ac366d00b26beab0874863980575be3875'
