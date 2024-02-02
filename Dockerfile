FROM registry.access.redhat.com/ubi9/python-39

ENV PYTHONUNBUFFERED=TRUE \
    GIT_SSL_NO_VERIFY="true" \
    PIP_INDEX_URL="https://nexus.spinks.work/repository/pypi/simple/" \
    PIP_TRUSTED_HOST="nexus.spinks.work"
USER root
RUN sed -i 's/enabled=1/enabled=0/' /etc/yum/pluginconf.d/subscription-manager.conf
RUN dnf update -y --security --nodocs --setopt install_weak_deps=False && \
    dnf clean all -y && \
    rm -rf /var/cache/yum && \
    mkdir /etc/confd && chmod 0700 /etc/confd && \
    rm -rf /etc/pki/rpm-gpg && \
    mkdir /etc/pki/rpm-gpg && \
    chmod 0644 /etc/pki/rpm-gpg
USER 1123
WORKDIR ${APP_ROOT}
COPY startup.sh app.py miro_team.py team_configs.py requirements.txt ./
RUN mkdir bin; \
  wget -O bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_x86_64; \ 
  chmod +x bin/dumb-init
RUN pip install -r requirements.txt
VOLUME secrets
EXPOSE 8443
ENTRYPOINT [ "./bin/dumb-init", "--" ]
CMD [ "bash", "-c", "source ./startup.sh && exec gunicorn -b 0.0.0.0:8443 --capture-output app:app"]
