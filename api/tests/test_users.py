from app.models import User
from uuid import UUID
from sqlalchemy import select

def test_create_user(client, session):
    # Test creating a new user
    response = client.post("/users/", json={"display_name": "testuser", "email": "testuser@example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["display_name"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "created_at" in data
    assert "id" in data

    db_user = session.get(User, UUID(data["id"]))
    assert db_user is not None
    assert db_user.email == "testuser@example.com"

def test_create_user_duplicate_email(client, session):
    # Test creating a user with a duplicate email
    first_response = client.post("/users/", json={"display_name": "testuser", "email": "testuser@example.com"})
    assert first_response.status_code == 201

    second_response = client.post("/users/", json={"display_name": "testuser2", "email": "testuser@example.com"})
    assert second_response.status_code == 400

    users = session.execute(select(User).where(User.email == "testuser@example.com")).scalars().all()
    assert len(users) == 1

def test_get_user(client):
    # Test retrieving an existing user
    create_response = client.post("/users/", json={"display_name": "testuser", "email": "testuser@example.com"})
    assert create_response.status_code == 201
    get_response = client.get(f"/users/{create_response.json()['id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["display_name"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_get_user_not_found(client):
    # Test retrieving a non-existent user
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

def test_update_user(client, session):
    # Test updating an existing user
    create_response = client.post("/users/", json={"display_name": "testuser", "email": "testuser@example.com"})
    assert create_response.status_code == 201
    update_response = client.patch(f"/users/{create_response.json()['id']}", json={"display_name": "updateduser", "email": "updateduser@example.com"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["display_name"] == "updateduser"
    assert data["email"] == "updateduser@example.com"

def test_update_user_not_found(client):
    # Test updating a non-existent user
    response = client.patch("/users/00000000-0000-0000-0000-000000000000", json={"display_name": "updateduser", "email": "updateduser@example.com"})
    assert response.status_code == 404

def test_delete_user(client, session):
    # Test deleting an existing user
    create_response = client.post("/users/", json={"display_name": "testuser", "email": "testuser@example.com"})
    assert create_response.status_code == 201
    delete_response = client.delete(f"/users/{create_response.json()['id']}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/users/{create_response.json()['id']}")
    assert get_response.status_code == 404