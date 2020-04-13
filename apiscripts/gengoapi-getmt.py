#!/usr/bin/python3
# -*- coding: utf-8 -*-
from hashlib import sha1
import hmac
import json
import requests
import time
PUBLIC_KEY = 'qHIvPPA=RDz@-cqLNdUWv_=52R2OdIHiGrYmtLyMm|^NOcAzC0j(zM[mpa~kTC$-'
PRIVATE_KEY = 's]|xRMswazI@NG7({79Cvk|gb)vzMXEkdc=3|PG-9fQZFw7aXVraPKz5=YCJRxvl'
# response type is currently JSON; can be changed to format of our choice
RESPONSE_TYPE = 'json'
header = {"Accept": "application/{0}".format(RESPONSE_TYPE)}
if __name__ == '__main__':
    PUBLIC_KEY = 'qHIvPPA=RDz@-cqLNdUWv_=52R2OdIHiGrYmtLyMm|^NOcAzC0j(zM[mpa~kTC$-'
    PRIVATE_KEY = 's]|xRMswazI@NG7({79Cvk|gb)vzMXEkdc=3|PG-9fQZFw7aXVraPKz5=YCJRxvl'
    # using job endpoint as base url
    base_url = "http://api.sandbox.gengo.com/v2/translate/job/"
    # ID of job to be retrieved
    # current job ID references completed job (set as reviewable in sandbox)
    job_id = "3289180"
    URL = base_url + job_id
    header = {"Accept": "application/json"}
    data = {

        "api_key": PUBLIC_KEY,
        "api_sig": PRIVATE_KEY,
        "ts": str(int(time.time())),
        "pre_mt": 1
    }
    # use your private_key to create an hmac
    key = data["api_sig"]
    keyb = bytes(key, encoding='utf8')
    ts = data["ts"]
    tsb = bytes(ts, encoding='utf8')
    #sha1b = bytes(sha1, encoding='utf8')
    data["api_sig"] = hmac.new(
        keyb,
        tsb,
        sha1
    ).hexdigest()

    # submit get request via requests
    get_machine_translation = requests.get(URL, headers=header, params=data)
    res_json = json.loads(get_machine_translation.text)
    if not res_json["opstat"] == "ok":
        msg = "API error occured.\nerror msg: {0}".format(
            res_json["err"]
        )
        raise AssertionError(msg)
    else:
        print(res_json)
