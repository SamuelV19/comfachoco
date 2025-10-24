from models import User
import pytest

def test_password_hashing():
    u = User(username="t", full_name="Test")
    u.set_password("abc123")
    assert u.check_password("abc123")
    assert not u.check_password("wrong")
