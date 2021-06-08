from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import PostViewSet, CommentViewSet, CommentDetail, GroupViewSet, FollowViewSet

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename="post")
router.register(r'group', GroupViewSet)
router.register(r'follow', FollowViewSet, basename="follow")

urlpatterns = [
    path('posts/<int:pk>/comments/', CommentViewSet.as_view(actions={'post': "create",
                                                                     'get': "list"})),
    path('posts/<int:pk>/comments/<int:comment_pk>/', CommentDetail.as_view()),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
