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

   # @receiver(page_published)
   # def on_change(instance, **kwargs):
   #     print('=======================',instance,kwargs)
   #     return

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('footer'),
    ]

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
    print("SENDER.OBJECTS: ", sender.objects.get(pk=4).body)
    #print("ISNTANCE OBJ",instance.objects )
   #ender.objects.filter(pk=obj.pk).update(val=F('val') + 1)

# Register a receiver
page_published.connect(on_update)

