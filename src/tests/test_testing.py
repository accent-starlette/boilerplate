from starlette_auth.tables import User


def test_default_test_user_exists():
    assert User.query.count() == 1


def test_another_user_can_be_added():
    user = User(email="another@example.com", first_name="Another", last_name="User")
    user.save()
    assert User.query.count() == 2


def test_session_was_rolled_back_after_test():
    assert User.query.count() == 1
