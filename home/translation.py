from .models import TransHomePage
from modeltranslation.translator import TranslationOptions
from modeltranslation.decorators import register


@register(TransHomePage)
class TransHomePageTR(TranslationOptions):
    fields = (
        'body',
    )
