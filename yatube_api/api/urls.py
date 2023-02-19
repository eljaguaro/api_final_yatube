from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

router = DefaultRouter()


router.register('v1/follow', views.FollowViewSet, basename='follow')
router.register('v1/posts', views.PostViewSet)
router.register('v1/groups', views.GroupViewSet)
router.register((r'v1/posts/(?P<post_id>\d+)/comments'),
                views.CommentViewSet, basename='comment')

urlpatterns = [
    # path('v1/api-token-auth/', obtain_auth_token),
    path('v1/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
