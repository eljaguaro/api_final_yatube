from rest_framework import viewsets, permissions, filters
from django.core.exceptions import PermissionDenied
from posts.models import User, Post, Group, Comment, Follow
from .serializers import CommentSerializer, FollowSerializer
from .serializers import PostSerializer, GroupSerializer
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsAuthorOrReadOnly
from django.core.exceptions import BadRequest


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author")
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, post):
        if post.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(PostViewSet, self).perform_destroy(post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, pk=post_id)
        new_queryset = (
            Comment.objects.filter(post=post).select_related("author"))
        return new_queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        serializer.save(author=self.request.user,
                        post=Post.objects.get(id=post_id))

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(CommentViewSet, self).perform_update(serializer)

    def perform_destroy(self, post):
        if post.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(CommentViewSet, self).perform_destroy(post)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        new_queryset = (
            Follow.objects.filter(user=self.request.user))
        return new_queryset

    def perform_create(self, serializer):
        following = (
            User.objects.get(username=self.request.data.get('following')))
        f = Follow.objects.filter(user=self.request.user, following=following)
        if f.count() == 0 and following != self.request.user:
            serializer.save(user=self.request.user, following=following)
        else:
            raise BadRequest('Invalid request.')

    def perform_destroy(self, follow):
        if follow.user != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(FollowViewSet, self).perform_destroy(follow)
