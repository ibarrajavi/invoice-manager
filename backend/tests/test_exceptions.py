from app.exceptions import AddressConflictError, AddressNotFoundError


def test_address_error_sets_attributes_and_message():
    err = AddressNotFoundError(3, 5)

    assert err.address_id == 3
    assert err.client_id == 5
    assert str(err) == "Address 3 not found for client 5."


def test_address_conflict_error_without_address_id():
    err = AddressConflictError(5)

    assert err.address_id is None
    assert err.client_id == 5
    assert str(err) == "New address for client 5 conflicts with an existing address."