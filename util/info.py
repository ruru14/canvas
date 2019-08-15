import os

dirname = os.path.dirname(__file__)

def getUserInfo():
    filename = os.path.join(dirname, 'user')
    file_user = open(filename, mode='rt', encoding='utf-8')
    lines_user = file_user.readlines()
    user = list()
    for line in lines_user:
        user.append(line.replace('\n', '').replace(' ', '').split(':'))
    return dict(user)

def getDbInfo():
    filename = os.path.join(dirname, 'profile')
    file_profile = open(filename, mode='rt', encoding='utf-8')
    liens_profile = file_profile.readlines()
    profile = list()
    for line in liens_profile:
        profile.append(line.replace('\n', '').replace(' ', '').split(':'))
    return dict(profile)