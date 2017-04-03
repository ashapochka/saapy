# dock-ca

Docked jenkins orchestrating assessment tasks and able to run other docker containers directly on the host

## How to Build

```
$ docker build -t saapy/jenkins .
```

## How to Run

Wiring *docker.sock* allows the docker client in the container to communicate to the host docker daemon.

```
$ docker run -d \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $DOCKER_MOUNT_HOME/saapy/jenkins.local.tdback.space/home:/var/jenkins_home \
    -p 8085:8080 saapy/jenkins
```
