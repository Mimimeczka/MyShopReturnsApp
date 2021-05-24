from django.urls import path, include
from rest_framework import routers
from ReturnsApp import views

router = routers.DefaultRouter()
router.register(r'returns', views.ReturnViewSet, basename='Return')

urlpatterns = [
    path('', include(router.urls)),
    path('returns/<int:return_id>/add/<int:product_id>/', views.add_product_to_return, name='add_product_to_return'),
    path('returns/<int:return_id>/delete/<int:product_id>/', views.delete_product_from_return, name='delete_product_from_return'),
    path('returns/<int:return_id>/summarize/', views.summarize_return, name='summarize_return'),
]