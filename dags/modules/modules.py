import requests
from datetime import datetime


def check_scheduler():
    """
    Test Airflow scheduler heartbeat
    """
    exec_time = datetime.now()
    msg = 'ran at {}'.format(exec_time)
    return msg

def check_network():
    """
    Test network connection within Docker container
    """
    # ping google
    r = requests.get('http://216.58.192.142')
    
    if r.status_code == 200:
        # network reachable inside container
        return 'connection ok'
    
    else:
        return 'no connection'