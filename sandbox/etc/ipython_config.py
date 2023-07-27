import environ

if environ.Env().bool('GUNICORN_RELOAD', default=False):
    print('--------->>>>>>>> AUTORELOAD ENABLED <<<<<<<<<------------')
    c.InteractiveShellApp.exec_lines = [  # noqa  # pylint: disable=undefined-variable
        '%load_ext autoreload',
        '%autoreload 2'
    ]
