FROM python:3.11.9-slim

USER root

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
        # Pre-compiled wheels don't exist for all the libraries we use on every platform, so we need compilers.
        gcc g++ \
        # Many of our requirements.txt files install libraries via git.
        git \
        # We need these mariadb packages for python to connect to mysql. mysqlclient also depends on pkg-config.
        mariadb-client libmariadb-dev pkg-config \
        sqlite3 \
        # Various dependencies for common requirements.
        libcurl4-openssl-dev libreadline-dev libssl-dev locales-all libffi-dev libxslt1-dev \
        # Essential unix utilities that don't come with the base Docker image we use.
        hostname less make procps psmisc tar telnet vim wget which \
    && \
    # Clean up after apt-get to reduce the size of this layer.
    apt-get clean && \
    # To ensure that bash is always used, we replace /bin/sh. Setting root's login shell won't work, due to an
    # implementation detail in deployfish related to FARGATE.
    ln -sf /bin/bash /bin/sh && \
    # Install supervisor globally so its executable and configs are in their default locations, rather than in the ve.
    /usr/local/bin/pip install supervisor && \
    # Add the users under which gunicorn and nginx will run.
    useradd -r gunicorn && \
    useradd -r nginx && \
    # Create the virtualenv for the app's python environment to live it.
    /usr/local/bin/python -m venv /ve && \
    # Generate a self-signed SSL cert for nginx to use.
    mkdir -p /certs && \
    openssl req -x509 -nodes \
      -subj "/C=US/ST=CA/O=Caltech/CN=localhost.localdomain" \
      -days 3650 \
      -newkey rsa:2048 \
      -keyout /certs/localhost.key \
      -out /certs/localhost.crt

# Ensure that we run the pip and python that are in the virtualenv, rather than
# the system copies.
ENV PATH /ve/bin:/app:$PATH

# Install the latest pip and our dependencies into the virtualenv.  We do this
# before copying the codebase so that minor code changes don't force a rebuild
# of the entire virtualenv.
COPY requirements.txt /tmp/requirements.txt
COPY django-sphinx-hosting.tar.gz /tmp/django-sphinx-hosting.tar.gz
RUN pip install --upgrade pip wheel && \
    pip install -r /tmp/requirements.txt && \
    pip install /tmp/django-sphinx-hosting.tar.gz

COPY . /app
WORKDIR /app

RUN pip install -e . && \
    # Precompile the sass files.
    python manage.py compilescss --settings=demo.settings_docker -v0 --skip-checks --use-storage && \
    # Run collectstatic to symlink all the static files into /static, which is
    # where the webserver expects them.
    python manage.py collectstatic --settings=demo.settings_docker --noinput -v0 && \
    chown -R gunicorn:nginx /static && \
    chown -R gunicorn:nginx /media && \
    # Symlink our configs into their default system locations.
    ln -sf /app/etc/supervisord.conf /etc/supervisord.conf && \
    ln -sf /app/etc/nginx.conf /etc/nginx/nginx.conf && \
    # Create an iPython profile and then replace the default config with our own, which enables automatic code reload.
    ipython profile create && \
    cp /app/etc/ipython_config.py /etc/ipython/profile_default/ipython_config.py

EXPOSE 443

ENTRYPOINT ["/bin/bash", "/app/bin/entrypoint.sh"]
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]