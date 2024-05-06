from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', checkService),
    path('check/', checkToken),
    path('extract-text/', extract_text_from_image, name='extract_text_from_image'),
    path('b64ToText/',b64Text)
]
