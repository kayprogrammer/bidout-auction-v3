from app.db.managers.general import review_manager
import pytest
import mock

BASE_URL_PATH = "/api/v3/general"


@pytest.mark.asyncio
async def test_retrieve_sitedetail(client):
    # Check response validity
    response = await client.get(f"{BASE_URL_PATH}/site-detail")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
    assert json_resp["message"] == "Site Details fetched"
    keys = ["name", "email", "phone", "address", "fb", "tw", "wh", "ig"]
    assert all(item in json_resp["data"] for item in keys)


@pytest.mark.asyncio
async def test_subscribe(client):
    # Check response validity
    response = await client.post(
        f"{BASE_URL_PATH}/subscribe", json={"email": "test_subscriber@example.com"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Subscription successful",
        "data": {"email": "test_subscriber@example.com"},
    }


@pytest.mark.asyncio
async def test_retrieve_reviews(client, verified_user, database):
    # Create test reviews
    review_dict = {
        "reviewer_id": verified_user.id,
        "show": True,
        "text": "This is a nice platform",
    }
    review_manager.create(database, review_dict)

    # Check response validity
    _, response = await client.get(f"{BASE_URL_PATH}/reviews")
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "message": "Reviews fetched",
        "data": [{"reviewer": mock.ANY, "text": "This is a nice platform"}],
    }
