from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    # path('success/', views.success, name='success'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
    path("auth/signup/", views.signup, name="signup"), #To keep it in same url range with other auths

]
