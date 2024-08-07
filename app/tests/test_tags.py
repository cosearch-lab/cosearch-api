from datetime import datetime


def test_create_tag(client):
    # create a new tag
    response = client.post(
        "/tags/",
        json={
            "display_name": "Test Tag",
            "color": "#FF0000",
        },
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    created_at = content.pop("created_at")
    updated_at = content.pop("updated_at")
    tag_id = content.pop("id")
    assert content == {
        "display_name": "Test Tag",
        "color": "#FF0000",
    }

    # verify that the tag was created in the database
    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": tag_id,
        "display_name": "Test Tag",
        "color": "#FF0000",
        "created_at": created_at,
        "updated_at": updated_at,
        "contributions": [],
    }

    # update the tag
    response = client.put(
        f"/tags/{tag_id}",
        json={
            "display_name": "Updated Tag",
            "color": "#00FF00",
        },
    )
    assert response.status_code == 200
    new_content = response.json()
    new_updated_at = new_content.pop("updated_at")
    assert new_content == {
        "id": tag_id,
        "display_name": "Updated Tag",
        "color": "#00FF00",
        "created_at": created_at,
    }
    assert datetime.fromisoformat(new_updated_at) > datetime.fromisoformat(updated_at)

    # verify that the tag was updated in the database
    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": tag_id,
        "display_name": "Updated Tag",
        "color": "#00FF00",
        "created_at": created_at,
        "updated_at": new_updated_at,
        "contributions": [],
    }
