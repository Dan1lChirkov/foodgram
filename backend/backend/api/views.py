from rest_framework import viewsets, filters, mixins, status
from django.shortcuts import get_object_or_404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action, api_view
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response

from recipes.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart,
    IngredientRecipie
)
from .permissioms import AuthorAdminOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipePostSerializer, RecipeGetSerializer,
    FavoriteSerializer, ShoppingCartSerializer,
    UserSubPresentSerializer, UserSubscribeSerializer,
    AvatarSerializer, RecipeShortLink,
    UserSelfSerializer
)
from .utils import create_model_instance, delete_model_instance
from .filters import RecipeFilter, IngredientFilter
from users.models import User, Subscription


class RecipieViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('pub_date')
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)
        if request.method == 'DELETE':
            error_message = 'Такого рецепта нет в избранном'
            return delete_model_instance(
                request, Favorite, recipe, error_message
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(
                request, recipe, ShoppingCartSerializer
            )
        if request.method == 'DELETE':
            error_message = 'Такого рецепта нет в списке покупок'
            return delete_model_instance(
                request, ShoppingCart, recipe, error_message
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipie.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount} {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny, ],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeShortLink(recipe, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class UserSubsriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSubPresentSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class UserSubscribeViewSet(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(
            user=request.user.id, author=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT', 'DELETE'])
def avatar(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'PUT':
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def me(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user = User.objects.get(id=request.user.id)
    serializer = UserSelfSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
