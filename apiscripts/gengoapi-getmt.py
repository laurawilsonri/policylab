#!/usr/bin/python3
# -*- coding: utf-8 -*-
from hashlib import sha1
import hmac
import json
import requests
import time
PUBLIC_KEY = 'LTT8cfNN(~GLH0[5FJ0IevYL3YH1Slg)^hkp@HG6{8_h9R)~]~lL3alSl@_YG76S'
PRIVATE_KEY = 'K9bphh_(Ovll^sO0~ZnEAoF5lMIm3-]ZhO8e[[sl)@QCfO$hpJ@ISVi$4rkGpFhX'
# response type is currently JSON; can be changed to format of our choice
RESPONSE_TYPE = 'json'
header = {"Accept": "application/{0}".format(RESPONSE_TYPE)}
if __name__ == '__main__':
    PUBLIC_KEY = 'LTT8cfNN(~GLH0[5FJ0IevYL3YH1Slg)^hkp@HG6{8_h9R)~]~lL3alSl@_YG76S'
    PRIVATE_KEY = 'K9bphh_(Ovll^sO0~ZnEAoF5lMIm3-]ZhO8e[[sl)@QCfO$hpJ@ISVi$4rkGpFhX'
    # using job endpoint as base url
    base_url = "http://api.sandbox.gengo.com/v2/translate/jobs/"
    # ID of job to be retrieved
    # current job ID references completed job (set as reviewable in sandbox)
    # job_id = "3289180"
    # URL = base_url + job_id
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

    # submit get request via requests: we are now getting the list of job ids
    get_machine_translation = requests.get(base_url, headers=header, params=data)
    res_json = json.loads(get_machine_translation.text)
    if not res_json["opstat"] == "ok":
        msg = "API error occured.\nerror msg: {0}".format(
            res_json["err"]
        )
        raise AssertionError(msg)
    else:
        resp = res_json.get("response")
        idstring = ""
        idlist = []
        # loop through all job ids!
        for r in resp:
            job_id = r.get("job_id")
            idstring = idstring + "," + str(job_id)
            idlist.append(str(job_id))
        # remove first comma from idstring :)
        idstring = idstring[1:]

        url = base_url + idstring
        # print(url)
        # header = {"Accept": "application/json"}
        data = {

            "api_key": PUBLIC_KEY,
            "api_sig": PRIVATE_KEY,
            "ts": str(int(time.time())),
            "pre_mt": 1,
            "id": idlist[0]
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

        data["data"] = json.dumps({'id': idlist[0]}, separators=(',', ':'))

        # submit get request via requests: we are now getting the actual
        # content of each job
        get_jobs = requests.get(url, headers=header, params=data)
        result_json = json.loads(get_jobs.text)
        if not result_json["opstat"] == "ok":
            msg = "API error occured.\nerror msg: {0}".format(
                result_json["err"]
            )
            raise AssertionError(msg)
        else:
            # print job response
            jobs = result_json.get("response").get("jobs")
            # print(jobs)
            for job in jobs:
                if "body_tgt" in job:
                    # print translated text
                    print(job.get("body_tgt"))
