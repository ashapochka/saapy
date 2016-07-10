import requests
import keyring
import anyconfig
import sys
import argparse


def set_neo4j_password(settings, neo4j_service, old_password, new_password):
    """
    sets new password for the neo4j server updating the server and the local keyring

    :param settings: configuration of the neo4j connection
    :param neo4j_service: neo4j instance name as in the configuration and keyring
    :param old_password: current password in neo4j database
    :param new_password: new password to set
    :return: None

    An excerpt from neo4j documentation on password change API:

    Changing the user password
    Given that you know the current password, you can ask the server to change a users password.
    You can choose any password you like, as long as it is different from the current password.

    Example request

    POST http://localhost:7474/user/neo4j/password
    Accept: application/json; charset=UTF-8
    Authorization: Basic bmVvNGo6bmVvNGo=
    Content-Type: application/json
    {
      "password" : "secret"
    }
    Example response

    200: OK
    """

    value_error_msg = ''

    if new_password == old_password:
        value_error_msg = "New password must not equal old password"
    elif not new_password:
        value_error_msg = "New password must not be empty"

    if value_error_msg:
        raise ValueError(value_error_msg)

    user_name = settings[neo4j_service]["user_name"]
    host_url = settings[neo4j_service]["service_url"]
    url = "{host_url}/user/{user_name}/password".format(host_url=host_url, user_name=user_name)
    headers = {"Accept": "application/json; charset=UTF-8",
               "Content-Type": "application/json"}
    payload = {'password': new_password}
    r = requests.post(url, auth=(user_name, old_password), headers=headers, json=payload)

    if r.ok:
        keyring.set_password(neo4j_service, user_name, new_password)
    else:
        r.raise_for_status()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("service", help="manage password for the service")
    parser.add_argument("old_password", help="provide the old password")
    parser.add_argument("new_password", help="provide the new password")
    args = parser.parse_args()
    settings = anyconfig.load("./conf/scripts-settings.yml")
    if "neo4j" in args.service:
        set_neo4j_password(settings, args.service, args.old_password, args.new_password)


if __name__ == '__main__':
    sys.exit(main())
