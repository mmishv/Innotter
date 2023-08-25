import pytest
from authentication.permissions import IsAdministrator, IsBlocked, IsModerator, IsUser
from tests.conftest import (
    base_request,
    invalid_jwt_request,
    mock_get_block_status,
    mock_get_role,
    test_credentials,
)


@pytest.mark.parametrize(
    "permission_cls, role, is_blocked, expected_permission",
    [
        (IsAdministrator, "ADMIN", False, True),
        (IsModerator, "MODERATOR", False, True),
        (IsUser, "USER", False, True),
        (IsBlocked, None, True, False),
        (IsBlocked, None, False, True),
        (IsAdministrator, None, False, False),
        (IsModerator, None, False, False),
        (IsUser, None, False, False),
        (IsBlocked, None, None, False),
        (IsAdministrator, None, None, False),
        (IsModerator, None, None, False),
        (IsUser, None, None, False),
    ],
)
def test_permissions(
    permission_cls,
    role,
    is_blocked,
    expected_permission,
    mock_get_role,
    mock_get_block_status,
    base_request,
    invalid_jwt_request,
):
    permission_instance = permission_cls()

    assert permission_instance.has_permission(invalid_jwt_request, None) is False
    assert (
        permission_instance.has_object_permission(invalid_jwt_request, None, None)
        is False
    )

    mock_get_role.return_value = role
    mock_get_block_status.return_value = is_blocked

    assert permission_instance.has_permission(base_request, None) == expected_permission
    assert (
        permission_instance.has_object_permission(base_request, None, None)
        == expected_permission
    )
