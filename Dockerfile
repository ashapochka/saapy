FROM saapy-base

USER root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install -yq --no-install-recommends \
    libglib2.0-dev \
    libxext6 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
    && /sbin/ldconfig -v

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_USER

COPY understand/Understand-4.0.854-Linux-64bit.tgz $HOME/Understand-4.0.854-Linux-64bit.tgz
RUN cd $HOME && tar -xvzf $HOME/Understand-4.0.854-Linux-64bit.tgz && rm $HOME/Understand-4.0.854-Linux-64bit.tgz
ENV UND_HOME $HOME/scitools
ENV PATH $PATH:$UND_HOME/bin/linux64
ENV PYTHONPATH $PYTHONPATH:$UND_HOME/bin/linux64/python
