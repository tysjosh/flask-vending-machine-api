from src.models import User


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """
    user = User('patkennedy79','patkennedy79@gmail.com', 'FlaskIsAwesome')
    assert user.email == 'patkennedy79@gmail.com'
    assert user.password != 'FlaskIsAwesome'
    assert user.username == 'patkennedy79'