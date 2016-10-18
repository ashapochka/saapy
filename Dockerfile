FROM saapy-base

USER $NB_USER

COPY understand/Understand-4.0.854-Linux-64bit.tgz $HOME/Understand-4.0.854-Linux-64bit.tgz
RUN cd $HOME && tar -xvzf $HOME/Understand-4.0.854-Linux-64bit.tgz && rm $HOME/Understand-4.0.854-Linux-64bit.tgz
ENV UND_HOME $HOME/scitools
ENV PATH $PATH:$UND_HOME/bin/linux64
ENV PYTHONPATH $PYTHONPATH:$UND_HOME/bin/linux64/python
