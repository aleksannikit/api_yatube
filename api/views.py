from rest_framework import permissions, generics, viewsets, serializers
from django.shortcuts import get_object_or_404
from api.serializers import PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer
from .models import Post, Comment, Group, Follow, User


class OwnResourcePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [OwnResourcePermission, ]

    def get_queryset(self):
        queryset = Post.objects.all()
        group = self.request.query_params.get('group')
        if group:
            queryset = queryset.filter(group=group)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [OwnResourcePermission, permissions.IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        return post.comments

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "comment_pk"
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [OwnResourcePermission, permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [OwnResourcePermission, ]

    def get_queryset(self):
        queryset = Follow.objects.all()
        follower = self.request.query_params.get('search')
        if follower:
            user = get_object_or_404(User, username=follower)
            queryset = user.following.all().union(user.follower.all())
        return queryset

    def perform_create(self, serializer):
        following = User.objects.filter(username=self.request.data.get("following")).first()
        if not following:
            # пользователя не существует или пустое имя
            raise serializers.ValidationError("User not found!")

        exist_following = Follow.objects.filter(user=self.request.user, following=following)
        if exist_following:
            raise serializers.ValidationError("You've already followed")

        serializer.save(user=self.request.user, following=following)
