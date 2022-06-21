from fastapi import HTTPException
from starlette import status


def not_found(obj):
    if obj in None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def forbidden(obj):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)