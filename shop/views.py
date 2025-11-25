from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


import json
import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from .models import Product, Order, OrderItem
from django.db import transaction
from django.contrib.auth import get_user_model, logout

@csrf_protect
def signup(request):
    import logging
    logger = logging.getLogger(__name__)

    # Debugging CSRF tokens
    csrf_token_from_cookie = request.COOKIES.get('csrftoken', '')
    csrf_token_from_post = request.POST.get('csrfmiddlewaretoken', '')
    logger.info(f"CSRF token in cookie: {csrf_token_from_cookie}")
    logger.info(f"CSRF token in form POST data: {csrf_token_from_post}")
    
    # Log cookie header
    cookie_header = request.META.get('HTTP_COOKIE', '')
    logger.info(f"HTTP_COOKIE header: {cookie_header}")
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")   # redirect to index
        else:
            # Return simple debug response showing form errors and CSRF tokens
            return HttpResponse(f"Form errors: {form.errors}<br>CSRF cookie: {csrf_token_from_cookie}<br>CSRF post token: {csrf_token_from_post}")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})



stripe.api_key = settings.STRIPE_SECRET_KEY

# -----------------------
# Async index view (non-blocking)
# -----------------------
from asgiref.sync import sync_to_async

from asgiref.sync import sync_to_async
from django.shortcuts import render
from .models import Product, Order

async def index(request):
    # Access request.user in a thread
    user = await sync_to_async(lambda: request.user)()

    # ORM → must use sync_to_async because ORM is not async
    products = await sync_to_async(list)(
        Product.objects.order_by("id").all()
    )
    orders = await sync_to_async(list)(
        Order.objects.filter(status="paid").order_by("-created_at")[:20]
    )

    context = {
        "products": products,
        "orders": orders,
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
        "user": user,  # important: pass explicitly so template doesn't lazily evaluate
    }

    # Rendering must be sync
    return await sync_to_async(render)(request, "shop/index.html", context)



# -----------------------
# Create checkout session (async view that delegates blocking calls)
# -----------------------
@require_POST
async def create_checkout_session(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json'}, status=400)

    items = data.get('items', [])
    if not items:
        return JsonResponse({'error': 'no items'}, status=400)

    # Build line_items by fetching products (sync) via sync_to_async
    line_items = []
    for it in items:
        try:
            p = await sync_to_async(Product.objects.get)(pk=int(it['product_id']))
        except Exception:
            continue
        qty = max(0, int(it.get('quantity', 0)))
        if qty <= 0:
            continue
        line_items.append({
            'price_data': {
                'currency': p.currency,
                'product_data': {'name': p.name},
                'unit_amount': p.price_cents,
            },
            'quantity': qty,
        })

    if not line_items:
        return JsonResponse({'error': 'no valid items'}, status=400)

    # Create Stripe checkout session — blocking call; run in thread via sync_to_async
    def _create_session():
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/?session_id={CHECKOUT_SESSION_ID}'),
            cancel_url=request.build_absolute_uri('/'),
        )

    try:
        session = await sync_to_async(_create_session, thread_sensitive=True)()
    except Exception as e:
        return JsonResponse({'error': 'stripe error', 'details': str(e)}, status=500)

    # Return session id to client
    return JsonResponse({'id': session.id})


# -----------------------
# Webhook: synchronous for DB transactions & idempotency
# -----------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest()

    # handle checkout.session.completed (or payment_intent.succeeded depending on flow)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        amount_total = int(session.get('amount_total') or 0)

        # Idempotent creation using transaction.atomic + get_or_create.
        # If webhook is retried, get_or_create prevents duplicate order creation.
        with transaction.atomic():
            order, created = Order.objects.get_or_create(
                stripe_session_id=session_id,
                defaults={'amount_total_cents': amount_total, 'paid': True}
            )
            if created:
                # fetch line items from Stripe (blocking call)
                try:
                    line_items = stripe.checkout.Session.list_line_items(session_id)
                except Exception:
                    # decide whether to rollback or not; for now, leave order created and log
                    line_items = []

                for li in line_items:
                    prod_name = li.description or (li.price.product if hasattr(li, 'price') else None)
                    # match by product name
                    try:
                        p = Product.objects.get(name=li.description or li.price.product)
                    except Product.DoesNotExist:
                        # skip unknown items (could also store fallback)
                        continue
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        quantity=li.quantity,
                        price_cents=li.price.unit_amount if hasattr(li.price, 'unit_amount') else 0
                    )

    # Always return 200 to acknowledge receipt
    return HttpResponse(status=200)




