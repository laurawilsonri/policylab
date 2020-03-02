from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class TransHomePage(Page):
    body = RichTextField(blank=True, default="")

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
