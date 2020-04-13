#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import sha1
import hmac
import json
import requests
import time

if __name__ == '__main__':
    PUBLIC_KEY = 'qHIvPPA=RDz@-cqLNdUWv_=52R2OdIHiGrYmtLyMm|^NOcAzC0j(zM[mpa~kTC$-'
    PRIVATE_KEY = 's]|xRMswazI@NG7({79Cvk|gb)vzMXEkdc=3|PG-9fQZFw7aXVraPKz5=YCJRxvl'
    # use jobs endpoint to submit jobs
    URL = "http://api.sandbox.gengo.com/v2/translate/jobs"
    header = {"Accept": "application/json"}

    data = {
        "api_key": PUBLIC_KEY,
        "api_sig": PRIVATE_KEY,
        "ts": str(int(time.time()))
    }
    # use your private_key to create an hmac
    print(data["api_sig"])
    key = data["api_sig"]
    keyb = bytes(key, encoding='utf8')
    ts = data["ts"]
    tsb = bytes(ts, encoding='utf8')
    print(sha1)
    #sha1b = bytes(sha1, encoding='utf8')
    data["api_sig"] = hmac.new(
        keyb,
        tsb,
        sha1
    ).hexdigest()

    job1 = {
        # slug = internal job name
        'slug': 'beep',
        # body = text to translate
        'body_src': 'We’re at the center of Rhode Island’s infrastructure for evidence-based policymaking.',
        #lc_src = source language
        'lc_src': 'en',
        #lc_tgt = target language
        'lc_tgt': 'es',
        #tier=quality level (standard vs pro)
        'tier': 'standard',
        #auto_approve = whether or not translation will be automatically approved
        # by the client (us)(for testing purposes)
        'auto_approve': 1,
        # comment = anything we want them to know
        'comment': 'This is a better comment',
        # purpose = what is the purpose of the job
        'purpose': 'Web localization',
        # pre_mt = whether or not to return a machine translation if translation
        # isn't ready yet. currently set to 1 for testing.
        'pre_mt': 1
        # ****FUTURE PARAMS WE MAY USE******:
        # callback_url: the url where system responses, comments, etc will be posted
        # attachments: this is where we can attach any files we may want, such as a glossary or video content
        # custom_data: where we may attach any extra data for the translator's reference
    }
    job2 = {
        # see job1 for descriptions of each param!
        'slug': 'boop',
        'body_src': 'Let’s learn together.',
        'lc_src': 'en',
        'lc_tgt': 'es',
        'tier': 'standard',
        'pre_mt': 1
    }

    # gather jobs together for submission
    jobs = {'job_1': job1, 'job_2': job2}
    data["data"] = json.dumps({'jobs': jobs}, separators=(',', ':'))

    #submit job
    post_job = requests.post(URL, data=data, headers=header)
    res_json = json.loads(post_job.text)
    if not res_json["opstat"] == "ok":
        msg = "API error occured.\nerror msg: {0}".format(
            res_json["err"]
        )
        raise AssertionError(msg)
    else:
        print(res_json)
