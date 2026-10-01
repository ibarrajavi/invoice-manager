import pytest
from app.exceptions import (
    ClientActiveStateError,
    ClientEmailError,
    ClientNameError,
    ClientNotFoundError,
    RequiredFieldError,
)
from app.models import Client
from app.services import clients as svc
from sqlalchemy import select


def test_clean_strips_whitespace():
    var = "  Javi "
    clean_var = svc._clean(var)

    assert clean_var == "Javi"


def test_clean_returns_none():
    var = None
    clean_var = svc._clean(var)

    assert clean_var is None


def test_require_strips_whitespace():
    var = "  Kanika   "
    field = "fname"

    required_var = svc._require(var, field)

    assert required_var == "Kanika"


def test_require_empty_value():
    var = None
    field = "fname"

    with pytest.raises(RequiredFieldError):
        svc._require(var, field)


def test_clean_email_lowercase():
    var = "  IbarraJavi@gmail.com "
    clean_var = svc._clean_email(var)

    assert clean_var == "ibarrajavi@gmail.com"


def test_clean_email_returns_none():
    var = None
    clean_var = svc._clean_email(var)

    assert clean_var is None


def test_has_name_returns_true():
    fname = "Javi"
    lname = "Ibarra"
    company_name = None

    has_name = svc._has_name(fname, lname, company_name)

    assert has_name == True


def test_has_name_returns_false():
    fname = "Javi"
    lname = None
    company_name = None

    has_name = svc._has_name(fname, lname, company_name)

    assert has_name == False


def test_set_active_client_false(db):
    client = svc.create_client(
        db,
        fname="Kanika",
        lname="Sun",
        email="kanika@test.com",
        phone="1234567890",
        company_name="Test Co",
    )

    svc._set_active(db, client.id, False)

    assert client.active == False


def test_set_active_client_true(db):
    client = svc.create_client(
        db,
        fname="Kanika",
        lname="Sun",
        email="kanika@test.com",
        phone="1234567890",
        company_name="Test Co",
    )

    svc._set_active(db, client.id, False)
    svc._set_active(db, client.id, True)

    assert client.active == True


def test_set_active_client_not_found(db):
    with pytest.raises(ClientNotFoundError):
        svc._set_active(db, 999, True)


def test_set_active_client_state_error(db):
    client = svc.create_client(
        db,
        fname="Kanika",
        lname="Sun",
        email="kanika@test.com",
        phone="1234567890",
        company_name="Test Co",
    )

    with pytest.raises(ClientActiveStateError):
        svc._set_active(db, client.id, True)


def test_successful_create_client(db):
    client = svc.create_client(
        db,
        fname="Javi",
        lname="Ibarra",
        email="javi@test.com",
        phone="1231231234",
        company_name="Test Co",
    )

    db.expire_all()
    stored = db.scalar(select(Client).where(Client.id == client.id))

    assert stored is not None
    assert stored.id == 1
    assert stored.fname == "Javi"
    assert stored.lname == "Ibarra"
    assert stored.email == "javi@test.com"
    assert stored.phone == "1231231234"
    assert stored.company_name == "Test Co"
    assert stored.active is True
    assert stored.setup_dt is not None


def test_create_client_requires_full_name_or_company(db):
    with pytest.raises(ClientNameError):
        svc.create_client(db, fname="Javi")


def test_email_is_case_sensitive(db):
    svc.create_client(db, fname="Kanika", lname="Sun", email="KanikaSun@gmail.com")
    with pytest.raises(ClientEmailError):
        svc.create_client(db, fname="Kani", lname="Sun", email="kanikasun@gmail.com")


def test_update_nonexistent_client(db):
    with pytest.raises(ClientNotFoundError) as exc_info:
        svc.update_client(db, 999, fname="Javier", lname="Test")

    assert exc_info.value.client_id == 999


def test_update_name_error(db):
    svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    with pytest.raises(ClientNameError):
        svc.update_client(db, 1, fname="Javier", lname=None)


def test_update_email_taken(db):
    svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    svc.create_client(db, fname="Kanika", lname="Sun", email="sun@testing.com")
    with pytest.raises(ClientEmailError):
        svc.update_client(db, 2, email="javi@testing.com")


def test_delete_nonexistent_client(db):
    with pytest.raises(ClientNotFoundError) as exc_info:
        svc.delete_client(db, 999)

    assert exc_info.value.client_id == 999


def test_successful_delete_client(db):
    user = svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    svc.create_client(db, fname="Kanika", lname="Sun", email="sun@testing.com")

    svc.delete_client(db, user.id)

    db.expire_all()

    client = db.scalar(select(Client).where(Client.id == user.id))

    assert client is None


def test_successful_deactivate_client(db):
    user = svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    svc.deactivate_client(db, user.id)

    assert user.active is False


def test_deactivate_client_active_state_error(db):
    user = svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    svc.deactivate_client(db, user.id)
    with pytest.raises(ClientActiveStateError):
        svc.deactivate_client(db, user.id)


def test_successful_activate_client(db):
    user = svc.create_client(db, fname="Kanika", lname="Sun", email="sun@testing.com")
    svc.deactivate_client(db, user.id)
    svc.activate_client(db, user.id)

    assert user.active is True


def test_activate_client_active_state_error(db):
    user = svc.create_client(db, fname="Kanika", lname="Sun", email="sun@testing.com")
    with pytest.raises(ClientActiveStateError):
        svc.activate_client(db, user.id)


def test_successful_get_client(db):
    user = svc.create_client(
        db, fname="Benito", lname="Ibarra", email="benito@testing.com"
    )
    get_client = svc.get_client(db, user.id)

    assert user.id == get_client.id


def test_successful_get_all_clients(db):
    clients = []
    clients.append(
        svc.create_client(db, fname="Javi", lname="Ibarra", email="javi@testing.com")
    )
    clients.append(
        svc.create_client(db, fname="Kanika", lname="Sun", email="sun@testing.com")
    )
    clients.append(
        svc.create_client(
            db, fname="Benito", lname="Ibarra", email="benito@testing.com"
        )
    )

    get_all_clients = svc.get_all_clients(db)

    assert clients[0].fname == get_all_clients[0].fname
    assert clients[1].fname == get_all_clients[1].fname
    assert clients[2].fname == get_all_clients[2].fname
