from datetime import datetime


def check_scheduler():
    exec_time = datetime.now()
    msg = 'ran at {}'.format(exec_time)

    return msg