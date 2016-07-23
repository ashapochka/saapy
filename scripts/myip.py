import requests


def myip():
    """
    retrieves external ip address of the pc running this function
    by calling http://myexternalip.com
    :return: external ip address as a string
    """
    url = 'http://myexternalip.com/raw'
    r = requests.get(url)
    ext_ip = r.text
    return ext_ip


if __name__ == '__main__':
    ip = myip()
    print(ip)
