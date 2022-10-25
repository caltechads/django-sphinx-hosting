import environ

if environ.Env().bool('GUNICORN_RELOAD', default=False):
    print('--------->>>>>>>> AUTORELOAD ENABLED <<<<<<<<<------------')
    c.InteractiveShellApp.exec_lines = [  # noqa
        '%load_ext autoreload',
        '%autoreload 2'
    ]
