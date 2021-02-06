from tweepy import OAuthHandler, API, Stream, StreamListener
from smtplib import SMTP_SSL
from config import *

# tweepy authentication  and setup
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = API(auth)

# generate ids for celebrities chosen in config.py file
CELEBRITY_IDS = [api.get_user(handle).id_str for handle in CELEBRITY_HANDLES]
CELEBRITIES = dict(zip(CELEBRITY_HANDLES, CELEBRITY_IDS))

# stores information wanted from a status update
class CelebrityTweet():
    def __init__(self, status) -> None:
        self.celebrity = status.user.name
        self.tweet = status.text
        self.urls =  status.entities["urls"]
        self.link = 'https://twitter.com/{}'.format(status.user.screen_name)

# emails tweet based on configuration in config.py
def email_tweet(tweet:CelebrityTweet) -> None:
    with SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

        subject = '{} just tweeted!'.format(tweet.celebrity)
        body = "{0} tweeted:\n\n{1}".format(tweet.celebrity, tweet.tweet)
        if tweet.urls:
            body += "\nThey linked {}".format(tweet.urls)
        body += "\n\nSee more here: {}".format(tweet.link)

        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(SENDER_EMAIL, EMAIL_RECIPIENTS, msg)

# override tweepy.StreamListener to send email when status updated
class CelebrityStreamListener(StreamListener):

    def on_status(self, status):
        ct = CelebrityTweet(status)
        email_tweet(ct)

# starts the user stream for specified celebrities
def start_stream():
    csl = CelebrityStreamListener()
    myStream = Stream(auth=api.auth, listener=csl)

    myStream.filter(follow=CELEBRITY_IDS)

if __name__ == "__main__":
    start_stream()