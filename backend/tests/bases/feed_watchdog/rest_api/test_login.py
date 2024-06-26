async def test_cant_login_with_wrong_password(client):
    response = await client.post(
        "/api/user/login", data={"username": "me@me.com", "password": "wrong"}
    )

    assert response.status_code == 400, response.text
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_can_login(client, admin_user):
    response = await client.post(
        "/api/user/login", data={"username": admin_user.email, "password": "12345678"}
    )

    result = response.json()

    assert response.status_code == 200, response.text
    assert "access_token" in result
    assert "refresh_token" in result
