from pathlib import Path
import shutil
import time
import anyconfig
import requests
import keyring


class Workspace:
    """
    represents an assessment workspace including local work directory
    with analyzed files.
    """

    def __init__(self, name, local_root_dir, work_dir=None, dry_run=False):
        self.name = name
        self.local_root_dir = Path(local_root_dir).resolve()
        self.work_dir_part = Path(work_dir or name)
        self.work_dir = self.local_root_dir / self.work_dir_part
        self.conf_dir = self.work_dir / "conf"
        self.conf_file = self.conf_dir / "workspace.conf"
        if not dry_run:
            self.work_dir.mkdir(exist_ok=True)
            self.conf_dir.mkdir(exist_ok=True)
            if not self.conf_file.is_file():
                self.conf_file.write_text("""
                active_profile: local_dev
                local_dev:
                    neo4j_service: local_neo4j
                local_neo4j:
                    service_type: neo4j
                    service_url: http://localhost:7474
                    user_name: neo4j
                """, encoding="utf-8")
            self.configuration = anyconfig.load(self.conf_file)

    def __str__(self):
        return "<Workspace name='{0}' work_dir={1}>".format(self.name,
                                                            self.work_dir)

    @classmethod
    def from_home(cls, name, work_dir=None, dry_run=False):
        """
        creates workspace with root in the current user home directory
        :param name: workspace name
        :param work_dir: workspace directory relative to user home,
        substituted with ws name if empty
        :param dry_run: if true skips file system manipulations
        :return: initialized workspace
        """
        return cls(name, Path.home(), work_dir=work_dir, dry_run=dry_run)

    @classmethod
    def from_current(cls, name, work_dir=None, dry_run=False):
        return cls(name, Path("."), work_dir=work_dir, dry_run=dry_run)

    def touch(self, filename):
        filepath = self.work_dir / filename
        filepath.touch()
        return filepath

    def mkdir(self, dirname):
        dirpath = self.work_dir / dirname
        dirpath.mkdir(parents=True, exist_ok=True)
        return dirpath

    def archive(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        archive_name = "{0}_{1}".format(self.work_dir, timestr)
        shutil.make_archive(archive_name, "zip",
                            str(self.local_root_dir),
                            str(self.work_dir.name))

    def abs_path(self, filepath):
        return self.work_dir / filepath

    def abs_path_str(self, filepath):
        return str(self.abs_path(filepath))

    def save_configuration(self):
        anyconfig.dump(self.configuration, self.conf_file)

    def set_neo4j_password(self, neo4j_service, old_password, new_password):
        """
        sets new password for the neo4j server updating the server and the
        local keyring

        :param neo4j_service: neo4j instance name as in the configuration and
        keyring
        :param old_password: current password in neo4j database
        :param new_password: new password to set
        :return: None

        An excerpt from neo4j documentation on password change API:

        Changing the user password
        Given that you know the current password, you can ask the server to
        change a users password.
        You can choose any password you like, as long as it is different from
        the current password.

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

        user_name = self.configuration[neo4j_service]["user_name"]
        host_url = self.configuration[neo4j_service]["service_url"]
        url = "{host_url}/user/{user_name}/password".format(host_url=host_url,
                                                            user_name=user_name)
        headers = {"Accept": "application/json; charset=UTF-8",
                   "Content-Type": "application/json"}
        payload = {'password': new_password}
        r = requests.post(url, auth=(user_name, old_password), headers=headers,
                          json=payload)

        if r.ok:
            keyring.set_password(neo4j_service, user_name, new_password)
        else:
            r.raise_for_status()
