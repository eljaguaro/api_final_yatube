import base64
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from posts.models import User, Comment, Post, Group, Follow
from django.core.files.base import ContentFile
from django.core.exceptions import SuspiciousOperation


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'post', 'text', 'author', 'created')
        read_only_fields = ('id', 'post', 'author', 'created')
        model = Comment


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'title', 'slug', 'description')
        read_only_fields = ('id', 'title', 'slug', 'description')
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    following = serializers.SlugRelatedField(slug_field='username',
                                             queryset=User.objects.all())

    class Meta:
        fields = ('user', 'following')
        read_only_fields = ('user',)
        model = Follow

    def validate(self, data):
        following = data['following']
        user = self.context['request'].user
        f = Follow.objects.filter(user=user, following=following)
        if f.count() > 0 or following == user:
            raise SuspiciousOperation("Ошибка запроса")
        return data
