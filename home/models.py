#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from django.dispatch import receiver
from wagtail.core.signals import page_published
from django.shortcuts import get_object_or_404
import sqlite3
import json


#from '../translate_text.py' import add_translation

from hashlib import sha1
import hmac
import json
import requests
import time

from apscheduler.schedulers.background import BackgroundScheduler


class TransHomePage(Page):
    body = RichTextField(blank=True, default="")
    footer = RichTextField(blank=True, default="")

    @receiver(page_published)
    def on_change(instance, **kwargs):
        print('=======================',instance,kwargs)
        return

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('footer'),
    ]

def submit_job(text_dict, target_lang):
    PUBLIC_KEY = '9VB[l8X1eYBp5NOkmSVq5Iw$(Jq2TVDX=Xy@9tHlurEq5MD{$qdN(99jVi_Llhc@'
    PRIVATE_KEY = '-(3GLORB[X]8Rw@@LZ2ch(Ieu](-m}y^g2vU3ty(jMly-D{yEAGq_smU{WY1xXJ0'
    # use jobs endpoint to submit jobs
    URL = "http://api.sandbox.gengo.com/v2/translate/jobs"
    header = {"Accept": "application/json"}

    data = {
        "api_key": PUBLIC_KEY,
        "api_sig": PRIVATE_KEY,
        "ts": str(int(time.time()))
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

    iter = 0
    joblist = []

    for thing in text_dict.items():
        # each item is of format: {"label": field_label, "text": field_text, "pk": int(page.pk), "table_name": table_name}
        item = thing[1]
        print(item)

        field_name = item.get('label')
        orig_text = item.get ('text')
        page_id = item.get('pk')
        table_name = item.get('table_name')

        print('||||||||||||||||||||||||||||||||||||||||||||| \n')
        print(field_name)
        print(orig_text)
        print(page_id)
        print(table_name)
        print('||||||||||||||||||||||||||||||||||||||||||||| \n')

        jobname = str('job' + str(iter))
        iter += 1


        custom_data = {"table_name":table_name, "field_name": field_name, "page_id": page_id, "target_lang": str(target_lang)}
        custom_data = json.dumps(custom_data)


        job = {
            # slug = internal job name
            'slug': field_name,
            # body = text to translate
            'body_src': str(orig_text),
            #lc_src = source language
            'lc_src': 'en',
            #lc_tgt = target language
            'lc_tgt': str(target_lang),
            #tier=quality level (standard vs pro)
            'tier': 'standard',
            #auto_approve = whether or not translation will be automatically approved
            # by the client (us)(for testing purposes)
            'auto_approve': 1,
            # purpose = what is the purpose of the job
            'purpose': 'Web localization',
            # pre_mt = whether or not to return a machine translation if translation
            # isn't ready yet. currently set to 1 for testing.
            'pre_mt': 1,
            # ****FUTURE PARAMS WE MAY USE******:
            # callback_url: the url where system responses, comments, etc will be posted
            # attachments: this is where we can attach any files we may want, such as a glossary or video content
            # custom_data: where we may attach any extra internal data
            'custom_data': custom_data
        }
        print(job)
        joblist.append(job)

    print(joblist)
    data["data"] = json.dumps({'jobs': joblist}, separators=(',', ':'))

    #submit job
    post_job = requests.post(URL, data=data, headers=header)
    res_json = json.loads(post_job.text)
    if not res_json["opstat"] == "ok":
        msg = "API error occured.\nerror msg: {0}".format(
            res_json["err"]
        )
        raise AssertionError(msg)
    else:
        print("success")
        print(res_json)



# Called when page is published.
def on_update(sender, **kwargs):
    page = kwargs['instance']
    revision = kwargs['revision']
    print("=================================")

    # get difference between revisions
    revisions = page.revisions.order_by('-created_at', 'id')
    prev_revision = revisions[1].as_page_object()
    latest_revision = revision.as_page_object()

    comparison = page.get_edit_handler().get_comparison()
    comparison = [comp(prev_revision, latest_revision) for comp in comparison]
    comparison = [comp for comp in comparison if comp.has_changed()]

    table_name = str(page.content_type).replace(' ', '').replace('|', '_')

    # make dictionary of fields that were changed in form {field_name: text}
    changed_fields = {}
    for diff in comparison:
        # clean field_label to match database formatting
        field_label = diff.field_label().replace('[', '').replace(']', '').replace(' ', '_')

        # only submit field_labels that are English
        if field_label.endswith("en"):
            field_text = get_field_val(table_name, str(field_label), int(page.pk))

            # currently Titles aren't stored in the database, so they will be null
            if field_text:
                changed_fields[field_label] = {"label": field_label, "text": field_text, "pk": int(page.pk), "table_name": table_name}

    print('********************************** \n')
    print(changed_fields)
    # submit translation job via 3rd party API
    if len(changed_fields) > 0:
        submit_job(changed_fields, "es")

#### DATABASE UPDATING #####

def get_field_val(table_name, field_name, pg_id):

    try:
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("db.sqlite3")

        # update that row in the table
        sql = '''SELECT ''' + field_name + ''' FROM ''' + table_name + ''' WHERE Page_ptr_id = ''' + str(pg_id) + ''';'''

        print(sql)

        # execute the sql command
        cur = con.cursor()
        cur.execute(sql)
        ans = cur.fetchall()
        con.commit()

        if ans and len(ans) > 0:
            return ans[0]

    except sqlite3.Error as e:
        return None


def add_translation(table_name, field_name, page_id, lang_code, translated_text):
    try:
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("db.sqlite3")

        if field_name.endswith("_en"):
            field_name = field_name[:-3]

        # update that row in the table
        sql = '''UPDATE ''' + table_name + '''
                SET ''' + field_name + '''_''' + lang_code + ''' = ?
                WHERE Page_ptr_id = ?'''

        # execute the sql command
        cur = con.cursor()
        cur.execute(sql, (translated_text, page_id))
        con.commit()
    except sqlite3.Error as e:
        print(e)
        print("ERROR: ", str(lang_code), " TRANSLATION FOR ", field_name, "COULD NOT BE UPDATED IN DATABASE.")

# Register a receiver that listens for when page is published
page_published.connect(on_update)


def retrieve_translation():
    PUBLIC_KEY = '9VB[l8X1eYBp5NOkmSVq5Iw$(Jq2TVDX=Xy@9tHlurEq5MD{$qdN(99jVi_Llhc@'
    PRIVATE_KEY = '-(3GLORB[X]8Rw@@LZ2ch(Ieu](-m}y^g2vU3ty(jMly-D{yEAGq_smU{WY1xXJ0'
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
                    # print(job.get("body_tgt"))
                    #print(job)
                    if "custom_data" in job:
                        print(job.get("custom_data"))
                        custom_data = json.loads(job.get("custom_data"))
                        table_name = custom_data.get("table_name")
                        print(table_name)
                        field_name = custom_data.get("field_name")
                        print("field_name", field_name)
                        page_id = custom_data.get("page_id")
                        print(page_id)
                        lang_code = custom_data.get("target_lang")
                        print(lang_code)
                        translated_text = job.get("body_tgt")[2:-3]
                        print(translated_text)
                        add_translation(table_name, field_name, page_id, lang_code, translated_text)

scheduler = BackgroundScheduler()
scheduler.add_job(retrieve_translation, 'interval', seconds=30)
scheduler.start()
