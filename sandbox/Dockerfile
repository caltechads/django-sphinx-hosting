FROM public.ecr.aws/m3v9w5i2/caltech-imss-ads/amazonlinux2-python3.10

USER root

ENV LC_ALL=en_US.utf8 LANG=en_US.utf8 PYCURL_SSL_LIBRARY=nss SHELL_PLUS=ipython IPYTHONDIR=/etc/ipython

RUN amazon-linux-extras install nginx1 rust1 python3.8 && \
    yum -y update && \
    yum -y install \
        gcc \
        glibc-locale-source \
        glibc-langpack-en \
        git \
        libcurl-devel \
        openssl-devel \
        # Even though we don't always use Apache in these apps, mod_ssl installs certs that we need.
        mod_ssl \
        # We need these mysql packages for python to be able to connect to mysql, and for `manage.py dbshell` to work.
        mysql-devel \
        mysql \
        # Useful unix utilities that don't come with the amazonlinux2 docker image.
        hostname \
        psmisc \
        procps-ng \
        which \
    && \
    # Cleanup for yum, as suggested by yum itself. Minimizes image size.
    yum -y clean all && \
    rm -rf /var/cache/yum && \
    # Set up the UTF-8 locale so that shelling into the container won't spam you with locale errors.
    localedef -i en_US -f UTF-8 en_US.UTF-8 && \
    # Install supervisor globally
    /opt/python/bin/pip3.10 install supervisor && \
    # Create the venv
    /opt/python/bin/python3.10 -m venv /ve && \
    # Add the user under which gunicorn will run.
    adduser -r gunicorn

# Ensure that we run the pip and python that are in the virtualenv, rather than the system copies.
ENV PATH /ve/bin:$PATH

# Install the latest pip and our dependencies into the virtualenv.  We do this
# before copying the codebase so that minor code changes don't force a rebuild
# of the entire virtualenv.
COPY requirements.txt /tmp/requirements.txt
COPY django-sphinx-hosting.tar.gz /tmp/django-sphinx-hosting.tar.gz
RUN pip install --upgrade pip wheel && \
    pip install -r /tmp/requirements.txt && \
    # Purge the pip cache, which can save us a good few megabytes in the docker image.
    rm -rf `pip cache dir`

COPY . /app
WORKDIR /app

# Install our app into the ve, symlink static resources, settings files, certs into place, etc.
RUN pip install -e . && \
    cp etc/supervisord.conf /etc/supervisord.conf && \
    cp etc/nginx.conf /etc/nginx/nginx.conf && \
    # Precompile the sass files.
    python manage.py compilescss --settings=demo.settings_docker -v0 --skip-checks --use-storage && \
    # Run collectstatic to symlink all the static files into /static, which is where the webserver expects them.
    python manage.py collectstatic --settings=demo.settings_docker --noinput -v0 && \
    chown -R gunicorn:nginx /static && \
    /usr/libexec/httpd-ssl-gencerts && \
    mkdir /certs && \
    cp /etc/pki/tls/private/localhost.key /certs && \
    cp /etc/pki/tls/certs/localhost.crt /certs && \
    chown gunicorn /certs/* && \
    # Create an iPython profile and then replace the default config with our own, which enables automatic code reload.
    ipython profile create && \
    cp /app/etc/ipython_config.py /etc/ipython/profile_default/ipython_config.py

EXPOSE 443

CMD ["/opt/python/bin/supervisord", "-c", "/etc/supervisord.conf"]