import json
import praw
import redis
import hashlib
from datetime import datetime
from fbchat import Client, Message, ThreadType
from fbchat._exception import FBchatUserError


def get_subreddit_top(**context):
    """
    Retrievs top 3 daily post urls from selected subreddits

    :return:    str
                sha256 hexdigest of data
    """
    with open('dags/configs/apikeys.json', 'r') as file:
        # load reddit api key from config file
        config = json.load(file)
        apikey = config['reddit']
    
    with open('dags/configs/targets.json', 'r') as file:
        # load target subreddits
        targets = json.load(file)
        subreddits = targets['subreddits']
    
    reddit = praw.Reddit(
        client_id=apikey['personal'],
        client_secret=apikey['secret'],
        user_agent=apikey['agent'],
        username=apikey['username'],
        password=apikey['password']
    )

    payload = {}

    for sub in subreddits:
        try:
            # fetch top 3 daily hot posts
            # from subreddits specified in conf file
            subreddit = reddit.subreddit(sub)
            payload[sub] = [submission.url for submission in subreddit.hot(limit=3)]
        
        except praw.exceptions.APIException:
            exmsg = 'Could not fetch posts from {}'.format(sub)
            raise praw.exceptions.APIException(exmsg)
    
    # hexdigest of data gives unique key
    # for each submission
    buffer = json.dumps(payload, sort_keys=True)
    m = hashlib.sha256()
    m.update(buffer.encode())
    digest = m.hexdigest()

    r = redis.StrictRedis(host='redis', port=6379, db=1)
    r.set(digest, buffer.encode())

    return digest


def push_message(**context):
    """
    Pushes fetched urls in form of
    formatted message using fb messenger

    :return:    int
                job exit code
    """
    # get hexdigest of latest pull by fetching
    # context of upstream task
    digest = context['task_instance'].xcom_pull(task_ids='get_reddit_hot')
    rfetch = redis.StrictRedis(host='redis', port=6379, db=1)
    rmeta = redis.StrictRedis(host='redis', port=6379, db=2)

    with open('dags/configs/apikeys.json', 'r') as file:
        # load facebook api key from config file
        config = json.load(file)
        apikey = config['fb']
    
    with open('dags/configs/targets.json', 'r') as file:
        # load target user ids
        targets = json.load(file)
        uids = targets['uids']
    
    with open('dags/configs/message.txt', 'r') as file:
        # load main message body
        msg = file.read()
    
    try:
        client = Client(
            email=apikey['user'],
            password=apikey['password']
        )
    
    except FBchatUserError:
        raise FBchatUserError('Could not log in')
    
    # get dict with urls from redis db
    subs_raw = rfetch.get(digest).decode('utf-8')
    subs = json.loads(subs_raw)

    for subname, urls in subs.items():
        # set next subreddit name as header
        msg += '\n\nr/{}'.format(subname)

        for idx, url in enumerate(urls):
            # add url to ordered list
            msg += '\n\n{}. {}'.format(idx + 1, url)
    
    for usrname, usrid in uids.items():
        try:
            # push msg body to user
            msgobj = Message(text=msg)
            client.send(msgobj, thread_id=usrid)

        except FBchatUserError:
            exmsg = 'Could not push for user: {}'.format(username)
            raise FBchatUserError(exmsg)
    
    date_sent = datetime.now()

    metadata = {
        'date': date_sent.strftime('%d.%m.%Y'),
        'time': date_sent.strftime('%H:%M:%S'),
        'users': list(uids.keys()),
        'digest': digest
    }

    # save metadata of last run under
    # ddmmYYYY key
    payload = json.dumps(metadata)
    rmeta.set(date_sent.strftime('%d.%m.%Y'), payload.encode())
    client.logout()

    return 0
