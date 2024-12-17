FROM python:3.11.10-slim AS build

# This part builds the virtual environment and installs the system dependencies
# needed to do so.

ENV UV_PROJECT_ENVIRONMENT=/ve

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install --yes --no-install-recommends \
        gcc g++ rustc cargo \
        # Some of our python dependencies come from github or gitlab
        git \
        # Mysql dependencies for mysqlclient
        mariadb-client libmariadb-dev pkg-config \
        # Various dependencies for common requirements.
        libcurl4-openssl-dev libreadline-dev libssl-dev locales-all libffi-dev libxslt1-dev \
    && \
    apt-get clean && \
    ln -sf /bin/bash /bin/sh && \
    /usr/local/bin/pip install --upgrade supervisor uv pip setuptools wheel

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/
COPY django-sphinx-hosting.tar.gz /_lock/
RUN cd /_lock && \
    uv sync --frozen --no-dev

FROM python:3.11.10-slim

ENV HISTCONTROL=ignorespace:ignoredups  \
    IPYTHONDIR=/etc/ipython             \
    LANG=en_US.UTF-8                    \
    LANGUAGE=en_US.UTF-8                \
    LC_ALL=en_US.UTF-8                  \
    LOGGING_MODE=print                  \
    # Disable the pip cache to reduce layer size.
    PIP_NO_CACHE_DIR=1                  \
    PYCURL_SSL_LIBRARY=nss              \
    SHELL_PLUS=ipython                  \
    # This env var overrides other system timezone settings.
    TZ=America/Los_Angeles


# We set this env var for this command only, so that installers know we're not running them interactively.
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install --yes --no-install-recommends \
        nginx \
        git \
        # We need these mariadb packages for python to connect to mysql. mysqlclient also depends on pkg-config.
        mariadb-client libmariadb-dev pkg-config \
        sqlite3 \
        # Various dependencies for common requirements.
        locales-all \
        # Essential unix utilities that don't come with the base Docker image we use.
        hostname less make procps psmisc tar telnet vim wget which \
    && \
    apt-get clean && \
    ln -sf /bin/bash /bin/sh && \
    /usr/local/bin/pip install --upgrade supervisor setuptools pip && \
    # Add the user under which supervisord, gunicorn, and nginx will run.
    adduser --disabled-password app && \
    # Create the directories that nginx needs to run.
    mkdir -p /var/tmp/nginx/client_body \
        /var/tmp/nginx/proxy \
        /var/tmp/nginx/fastcgi \
        /var/tmp/nginx/uwsgi \
        /var/tmp/nginx/scgi \
    && \
    # Generate a self-signed SSL cert for nginx to use.
    mkdir -p /certs && \
    openssl req -x509 -nodes \
      -subj "/C=US/ST=CA/O=Caltech/CN=localhost.localdomain" \
      -days 3650 \
      -newkey rsa:2048 \
      -keyout /certs/localhost.key \
      -out /certs/localhost.crt && \
    chown -R app:app /certs/*

COPY --from=build --chown=app:app /ve /ve
ENV PATH=/ve/bin:/usr/local/bin:$PATH

COPY . /app
WORKDIR /app

RUN python manage.py compilescss --settings=demo.settings_docker -v0 --skip-checks --use-storage && \
    # Run collectstatic to symlink all the static files into /static, which is
    # where the webserver expects them.
    python manage.py collectstatic --settings=demo.settings_docker --noinput -v0 && \
    chown -R app:app /app && \
    chown -R app:app /static && \
    chown -R app:app /media && \
    # Symlink our configs into their default system locations.
    ln -sf /app/etc/supervisord.conf /etc/supervisord.conf && \
    ln -sf /app/etc/nginx.conf /etc/nginx/nginx.conf && \
    # Create an iPython profile and then replace the default config with our own, which enables automatic code reload.
    ipython profile create && \
    cp /app/etc/ipython_config.py /etc/ipython/profile_default/ipython_config.py

EXPOSE 8443

USER app

ENTRYPOINT ["/bin/bash", "/app/bin/entrypoint.sh"]
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]