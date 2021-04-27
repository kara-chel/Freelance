import os
import random


def get_proxies_http():
    PROXIES_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.http.txt')
    with open(PROXIES_FILE) as fh:
        PROXIES = fh.read().splitlines()

    return(random.choice(PROXIES))


def get_proxies_https():
    PROXIES_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.https.txt')
    with open(PROXIES_FILE) as fh:
        PROXIES = fh.read().splitlines()

    return(random.choice(PROXIES))


if __name__ == '__main__':
    print(get_proxies_http())
    print(get_proxies_https())
