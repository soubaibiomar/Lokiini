from fastapi import HTTPException, status


def is_admin(user) -> bool:
    return user.user_role == "admin"


def require_resource_access(user, *allowed_user_ids) -> None:
    if not is_admin(user) and user.id not in allowed_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Vous n'êtes pas autorisé à accéder à cette ressource."},
        )


def require_owner(user, owner_id) -> None:
    require_resource_access(user, owner_id)
