import sys, platform
from app import app
if __name__ == '__main__':
    if platform.system() == 'Windows':
        from waitress import serve
        serve(app, listen='*:8080')
    else:
        from gunicorn.app.wsgiapp import run
        print(" OS System:",platform.system())
        sys.argv = "gunicorn --bind 0.0.0.0:5151 app:app".split()
        sys.exit(run())
