from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
)


class IsAdminOrReadOnly(BasePermission):

    def has_permission(
        self,
        request,
        view,
    ):

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        return (
            user
            and user.is_authenticated
            and (
                user.is_staff
                or user.is_superuser
                or user.role == "admin"
            )
        )