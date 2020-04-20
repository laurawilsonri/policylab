#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from django.dispatch import receiver
from wagtail.core.signals import page_published
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

def submit_job(orig_text, target_lang):
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

    job1 = {
        # slug = internal job name
        'slug': 'auto',
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

    jobs = {'job_1': job1}
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
        print("success")
        print(res_json)


def on_update(sender, **kwargs):
    instance = kwargs['instance']
    revision = kwargs['revision']
    print("=================================")
   # print("REVISION", revision)
   # print("REVISION_BODY_EN", revision.content_json)
   # print("SENDER: ", sender.body_en(field_name))
   # print("INSTANCE", instance.get_context)
   # print("PAGE_BODY_EN", instance.body_en)
    print("TYPE OF JSON", type(revision.content_json))
    submit_job(revision.content_json, "es")
    print("SENDER.OBJECTS: ", sender.objects.get(pk=4).body)
    #print("ISNTANCE OBJ",instance.objects )
   #ender.objects.filter(pk=obj.pk).update(val=F('val') + 1)

# Register a receiver
page_published.connect(on_update)
