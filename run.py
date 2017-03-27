# uwsgi --socket 127.0.0.1:8080 -w WSGI:app --master --processes 4 --threads 2  --daemonize log/uWSGI.log
import sys

sys.path.append('./')

from py_rmc import rmc


if __name__ == "__main__":
    # ddn_ep.run()
    rmc.run(debug=True)