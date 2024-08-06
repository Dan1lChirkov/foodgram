from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, RecipieViewSet, IngredientViewSet, UserSubsriptionViewSet,
    UserSubscribeViewSet, avatar, me
)


router = DefaultRouter()
router.register('recipes', RecipieViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/me/', me),
    path('users/me/avatar/', avatar),
    path('users/subscriptions/', UserSubsriptionViewSet.as_view(
        {'get': 'list'}
    )),
    path('users/<int:user_id>/subscribe/', UserSubscribeViewSet.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path("s/", include("urlshortner.urls")),
]
