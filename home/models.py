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


class TransHomePage(Page):
    body = RichTextField(blank=True, default="")
    footer = RichTextField(blank=True, default="")

   # @receiver(page_published)
   # def on_change(instance, **kwargs):
   #     print('=======================',instance,kwargs)
   #     return

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

    for item in text_dict.items():

        field_name = item[0]
        orig_text = item[1]

        jobname = str('job' + str(iter))
        iter += 1

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
            'pre_mt': 1
            # ****FUTURE PARAMS WE MAY USE******:
            # callback_url: the url where system responses, comments, etc will be posted
            # attachments: this is where we can attach any files we may want, such as a glossary or video content
            # custom_data: where we may attach any extra data for the translator's reference
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
        field_text = get_field_val(table_name, str(field_label), int(page.pk))

        # currently Titles aren't stored in the database, so they will be null
        if field_text:
            changed_fields[field_label] = {"label": field_label, "text": field_text, "pk": int(page.pk), "table_name": table_name}

    print(changed_fields)
    # submit translation job via 3rd party API
    submit_job(changed_fields, "es")


#### DATABASE UPDATING #####

def get_field_val(table_name, field_name, pg_id):

    try:
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("db.sqlite3")

        # update that row in the table
        sql = '''SELECT ''' + field_name + ''' FROM ''' + table_name + ''' WHERE Page_ptr_id = ''' + str(pg_id) + ''';'''

        # execute the sql command
        cur = con.cursor()
        cur.execute(sql)
        ans = cur.fetchall()
        con.commit()

        if ans and len(ans) > 0:
            return ans[0]

    except sqlite3.Error as e:
        return None


def add_translation(table_name, field_name, pg_id, lang_code, translated_text):
    try:
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect("db.sqlite3")

        # update that row in the table
        sql = '''UPDATE ''' + table_name + '''
                SET ''' + field_name + '''_''' + lang_code + ''' = ?
                WHERE Page_ptr_id = ?'''

        # execute the sql command
        cur = con.cursor()
        cur.execute(sql, (translated_text, pg_id))
        con.commit()
    except sqlite3.Error as e:
        print("ERROR: ", str(lang_code), " TRANSLATION FOR ", field_name, "COULD NOT BE UPDATED IN DATABASE.")


# Register a receiver that listens for when page is published
page_published.connect(on_update)
