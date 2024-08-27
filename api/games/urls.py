from django.urls import path
from rest_framework import routers
from .views import GameViewSet

router = routers.DefaultRouter()
router.register(r"", GameViewSet)

urlpatterns = router.urls
