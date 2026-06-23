from rest_framework import permissions


class IsBoardOwnerOrMember(permissions.BasePermission):
    """Permission für Board: Owner oder Member darf zugreifen"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()


class IsBoardOwner(permissions.BasePermission):
    """Permission für Board: nur Owner darf zugreifen"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsTaskBoardMember(permissions.BasePermission):
    """Permission für Task: User muss Mitglied des Boards sein"""

    def has_object_permission(self, request, view, obj):
        return request.user in obj.board.members.all()


class IsCommentAuthor(permissions.BasePermission):
    """Permission für Comment: nur Autor darf zugreifen"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
