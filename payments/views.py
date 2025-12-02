from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, permission_classes, api_view, authentication_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.conf import settings
from django.core.mail import send_mail
import time
from .models import Payment
from .serializers import PaymentSerializer
from translations.models import Translation, PendingTranslations
from translations.serializers import TranslationSerializer
from translations.email_service import send_translation_email
from django.utils.translation import gettext_lazy as _
import hmac, requests
import json
import hashlib
import logging
from datetime import datetime
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Payment


class WayForPay:
    API_URL = "https://api.wayforpay.com/api"
    MERCHANT_ACCOUNT = settings.WAYFORPAY_MERCHANT_ACCOUNT
    MERCHANT_SECRET_KEY = settings.WAYFORPAY_SECRET_KEY
    MERCHANT_DOMAIN = settings.WAYFORPAY_MERCHANT_DOMAIN

    @staticmethod
    def get_signature(data):
        sig_list = [
            data["merchantAccount"],
            data["merchantDomainName"],
            data["orderReference"],
            str(data["orderDate"]),
            data["amount"],
            data["currency"],
            data["productName"][0],
            str(data["productCount"][0]),
            data["productPrice"][0],
        ]
        sig_str = ";".join(sig_list)
        return hmac.new(WayForPay.MERCHANT_SECRET_KEY.encode(), sig_str.encode(),hashlib.md5).hexdigest()

    @staticmethod
    def get_answer_signature(merchant_key, data):
        order_reference = data["orderReference"]
        status = data["status"]
        time = data["time"]

        signature_text = f"{order_reference};{status};{time}"
        signature = hmac.new(merchant_key.encode("utf-8"), signature_text.encode("utf-8"), hashlib.md5).hexdigest()
        return signature

    @staticmethod
    def create_invoice(data):
        try:
            amt = float(data["amount"])
            pp = float(data["productPrice"][0])
            cnt = int(data["productCount"][0])

            formatted_amount = f"{amt:.2f}"
            formatted_price = f"{pp:.2f}"

            data["amount"] = formatted_amount
            data["productPrice"] = [formatted_price]
            data["productCount"] = [cnt]

            body = {
                "merchantSignature": WayForPay.get_signature(data),
                "merchantAccount": WayForPay.MERCHANT_ACCOUNT,
                "merchantDomainName": WayForPay.MERCHANT_DOMAIN,
                "transactionType": "CREATE_INVOICE",
                "apiVersion": 1,
                "language": "ua",
                "notifyMethod": "email",
                "orderReference": data["orderReference"],
                "orderDate": int(data["orderDate"]),
                "amount": formatted_amount,
                "currency": data["currency"],
                "productName": data["productName"],
                "productCount": [cnt],
                "productPrice": [formatted_price],
                "serviceUrl": data.get("serviceUrl"),
                "clientEmail": data.get("clientEmail"),
                "returnUrl": data.get("returnUrl"),
            }

            sig_list = [
                body["merchantAccount"],
                body["merchantDomainName"],
                body["orderReference"],
                str(body["orderDate"]),
                body["amount"],
                body["currency"],
                body["productName"][0],
                str(body["productCount"][0]),
                body["productPrice"][0],
            ]

            resp = requests.post(WayForPay.API_URL, json=body, headers={"Content-Type": "application/json"})

            resp_data = resp.json()

            return resp_data

        except Exception as e:
            raise RuntimeError(f"WayForPay invoice creation failed: {e}")


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "created_at"]
    ordering_fields = ["created_at", "amount", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_admin", False):
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        source_text = request.data.get("source_text")
        source_lang = request.data.get("source_lang")
        target_lang = request.data.get("target_lang")
        if not all([source_text, source_lang, target_lang]):
            return Response(
                {"error": "Source text, source language and target language are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = max(len(source_text) / 10, 1.00)
        serializer = self.get_serializer(
            data={
                'user': request.user.id,
                'amount': round(amount, 2),
                'status': Payment.PaymentStatus.PENDING,
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        PendingTranslations.objects.create(
            payment=payment,
            source_text=source_text,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        unique_ref = f"{payment.id}-{int(time.time())}"
        payment.order_reference = unique_ref
        payment.save(update_fields=['order_reference'])

        amt_str = f"{float(amount):.2f}"
        wayforpay_payload = {
            "merchantAccount": WayForPay.MERCHANT_ACCOUNT,
            "merchantDomainName": WayForPay.MERCHANT_DOMAIN,
            "orderReference": unique_ref,
            "orderDate": int(payment.created_at.timestamp()),
            "amount": amt_str,
            "currency": "UAH",
            "productName": ["Translation"],
            "productCount": [1],
            "productPrice": [amt_str],
            "language": "ua",
            "transactionType": "CREATE_INVOICE",
            "apiVersion": 1,
            "serviceUrl": f"https://{WayForPay.MERCHANT_DOMAIN}/api/wfp_callback/",
            "notifyMethod": "POST",
            "returnUrl": request.data.get("returnUrl"),
            "clientEmail": request.user.email,
        }

        invoice = WayForPay.create_invoice(wayforpay_payload)
        payment_url = invoice.get("invoiceUrl")
        print("📡 WayForPay full response:", invoice)
        print("👉 reasonCode:", invoice.get("reasonCode"))
        print("👉 reason:", invoice.get("reason"))

        if not payment_url:
            payment.status = Payment.PaymentStatus.FAILURE
            payment.closed_at = timezone.now()
            payment.save(update_fields=['status', 'closed_at'])
            return Response(
                {"error": "Failed to create payment URL", "details": invoice},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "payment_id": payment.id,
                "order_reference": unique_ref,
                "amount": payment.amount,
                "payment_url": payment_url,
                "source_text": source_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        return Response({"error": _("Payments cannot be updated")}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if not getattr(request.user, "is_admin", False):
            return Response({"error": _("Only admins can delete payments")}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_payments(self, request):
        payments = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        if payment.user != request.user and not getattr(request.user, "is_admin", False):
            return Response(
                {"error": _("You are not authorized to confirm this payment")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if payment.status != Payment.PaymentStatus.PENDING:
            return Response(
                {"error": _("Payment is already processed")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deepl_response = requests.post(
            "https://api-free.deepl.com/v2/translate",
            headers={"Authorization": f"DeepL-Auth-Key {settings.DEEPL_API_KEY}"},
            data={
                "text": request.data.get("source_text"),
                "source_lang": request.data.get("source_lang"),
                "target_lang": request.data.get("target_lang"),
            },
        )
        if deepl_response.status_code != 200:
            payment.status = Payment.PaymentStatus.FAILURE
            payment.closed_at = timezone.now()
            payment.save()
            return Response(
                {"error": _("Translation failed")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        translated_text = deepl_response.json().get("translations")[0].get("text")

        translation_data = {
            "source_text": request.data.get("source_text"),
            "translated_text": translated_text,
            "source_lang": request.data.get("source_lang"),
            "target_lang": request.data.get("target_lang"),
        }
        translation_serializer = TranslationSerializer(
            data=translation_data, context={"request": request, "payment": payment}
        )
        translation_serializer.is_valid(raise_exception=True)
        translation = translation_serializer.save()

        payment.status = Payment.PaymentStatus.SUCCESS
        payment.closed_at = timezone.now()
        payment.save()

        send_mail(
            subject=_("Your Translation"),
            message=f"Source: {translation.source_text}\nTranslated ({translation.target_lang}): {translation.translated_text}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.user.email],
            fail_silently=False,
        )

        return Response(
            {
                "status": payment.status,
                "closed_at": payment.closed_at,
                "translation": translation_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def wfp_callback(request):
    try:
        logger.debug("Request headers: %s", dict(request.headers))
        logger.debug("Request body: %s", request.body.decode('utf-8'))

        # Отримуємо дані від WayForPay
        try:
            if request.body:
                raw_body = request.body.decode('utf-8')
                data = json.loads(raw_body)
            elif request.POST:
                raw_data = next(iter(request.POST.keys()), '{}')
                data = json.loads(raw_data) if raw_data.startswith("{") else dict(request.POST)
            else:
                data = request.data
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Failed to parse request data: %s", str(e))
            return Response({"error": "Invalid request format"}, status=400)

        logger.info("WayForPay callback received: %s", data)

        order_ref = data.get("orderReference")
        reason_code = data.get("reasonCode")
        
        if not order_ref:
            logger.error("Missing orderReference in callback")
            return Response({"error": "Missing orderReference"}, status=400)

        # Знаходимо платіж
        try:
            payment = Payment.objects.get(order_reference=order_ref, status=Payment.PaymentStatus.PENDING)
        except Payment.DoesNotExist:
            logger.error("Payment not found for orderReference: %s", order_ref)
            return Response({"error": "Payment not found"}, status=404)

        now = int(datetime.now().timestamp())
        
        # Обробляємо успішну оплату
        if reason_code == 1100:
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.closed_at = timezone.now()
            payment.save()
            logger.info("Payment successful: orderReference=%s", order_ref)

            # Перекладаємо текст та відправляємо на пошту
            try:
                pending = payment.pending_translation
                if pending:
                    # Викликаємо DeepL API
                    dl_response = requests.post(
                        "https://api-free.deepl.com/v2/translate",
                        headers={"Authorization": f"DeepL-Auth-Key {settings.DEEPL_API_KEY}"},
                        data={
                            "text": pending.source_text,
                            "source_lang": pending.source_lang,
                            "target_lang": pending.target_lang,
                        },
                    )
                    dl_response.raise_for_status()
                    dl_data = dl_response.json()
                    translated = dl_data["translations"][0]["text"]

                    # Зберігаємо переклад в БД
                    serializer = TranslationSerializer(
                        data={
                            "source_text": pending.source_text,
                            "translated_text": translated,
                            "source_lang": pending.source_lang.upper(),
                            "target_lang": pending.target_lang.upper(),
                        },
                        context={"request": request, "payment_id": payment.id}
                    )
                    serializer.is_valid(raise_exception=True)
                    translation = serializer.save()

                    # Відправляємо email
                    if payment.user.email:
                        logger.info("Sending translation email to %s", payment.user.email)
                        send_translation_email(translation=translation, user=payment.user)

                    # Видаляємо pending translation
                    pending.delete()
                    logger.info("Translation completed successfully for payment %s", payment.id)

            except PendingTranslations.DoesNotExist:
                logger.warning("No pending translation found for payment %s", payment.id)
            except Exception as e:
                logger.error("Translation processing error: %s", str(e))
                payment.status = Payment.PaymentStatus.FAILURE
                payment.save()
        else:
            # Обробляємо неуспішну оплату
            payment.status = Payment.PaymentStatus.FAILURE
            payment.closed_at = timezone.now()
            payment.save()
            logger.info("Payment failed: orderReference=%s, reasonCode=%s", order_ref, reason_code)

        # Відповідаємо WayForPay
        answer = {
            "orderReference": order_ref,
            "status": "accept",
            "time": now
        }
        answer["signature"] = WayForPay.get_answer_signature(settings.WAYFORPAY_SECRET_KEY, answer)
        logger.debug("Response to WayForPay: %s", answer)
        return Response(answer)

    except Exception as e:
        logger.error("Callback processing error: %s", str(e))
        return Response({"error": str(e)}, status=500)
