from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
import requests

class Translation(models.Model):
    class Language(models.TextChoices):
        EN = "EN", _("English")
        UK = "UK", _("Ukrainian")
        FR = "FR", _("French")
        GE = "GE", _("German")
        ES = "ES", _("Spanish")

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="translations", verbose_name=_("user"))
    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE, related_name="translations", verbose_name=_("payment"))
    source_text = models.TextField(_("source text"))
    translated_text = models.TextField(_("translated text"))
    source_lang = models.CharField(_('source language'), max_length=15, choices=Language.choices)
    target_lang = models.CharField(_('target language'), max_length=15, choices=Language.choices)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def clean(self):
        if len(self.source_text) > 50000:
            raise ValidationError(_("Source text must be less than 50000 characters"))
        if self.source_lang == self.target_lang:
            raise ValidationError(_("Source and target languages must be different"))

    def save(self, *args, **kwargs):
        if not self.translated_text and self.payment and self.payment.status == self.payment.PaymentStatus.SUCCESS:
            api_key = settings.DEEPL_API_KEY
            url = "https://api-free.deepl.com/v2/translate"
            params = {
                "auth_key": api_key,
                "text": self.source_text,
                "source_lang": self.source_lang,
                "target_lang": self.target_lang
            }
            response = requests.post(url, data=params)
            if response.status_code == 200:
                self.translated_text = response.json()['translations'][0]['text']
        super().save(*args, **kwargs)

    class Meta:
        db_table = "translations"
        verbose_name = _("translation")
        verbose_name_plural = _("translations")
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{_('Translation')} {self.pk} {_('for')} {self.user.username}"

class PendingTranslations(models.Model):
    payment = models.OneToOneField("payments.Payment", on_delete=models.CASCADE, related_name="pending_translation")
    source_text = models.TextField()
    source_lang = models.CharField(max_length=5000)
    target_lang = models.CharField(max_length=5000)

    def __str__(self):
        return f'Pending for Payment {self.payment.id}'