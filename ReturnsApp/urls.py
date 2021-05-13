from django.urls import path, include
from rest_framework import routers
from ReturnsApp import views

router = routers.DefaultRouter()
router.register(r'returns', views.ReturnViewSet, basename='Return')

urlpatterns = [
    path('', include(router.urls))
]