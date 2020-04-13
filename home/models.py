from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from django.dispatch import receiver
from wagtail.core.signals import page_published
#from '../translate_text.py' import add_translation


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
