from django.contrib import admin
from django.urls import path, include
from shop import views as shop_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # override logout first so it takes precedence
    path('auth/logout/', shop_views.logout_view, name='logout'),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('shop.urls')),
]