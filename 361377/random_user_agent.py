import os
import random

def get_user_agent():

    USER_AGENTS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'useragents.txt')
    with open(USER_AGENTS_FILE) as fh:
        USER_AGENTS = fh.read().splitlines()

    return(random.choice(USER_AGENTS))

if __name__ == '__main__':
    print(get_user_agent())
