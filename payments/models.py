from django.db import models
from django.utils.translation import gettext_lazy as _

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCESS = 'success', _('Success')
        FAILURE = 'failure', _('Failure')

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="payments", verbose_name=_("user"))
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    status = models.CharField(_("status"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    closed_at = models.DateTimeField(_("closed at"), null=True, blank=True)
    order_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)

    class Meta:
        db_table = "payments"
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{_('Payment')} {self.pk} {_('for')} {self.user.username}"