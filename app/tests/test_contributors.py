from datetime import datetime


def test_create_contributor(client):
    # create a new contributor
    response = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle",
            "display_name": "Test Display Name",
        },
    )
    assert response.status_code == 200
    content = response.json()
    created_at = content.pop("created_at")
    updated_at = content.pop("updated_at")
    contributor_id = content.pop("id")
    assert content == {
        "local_handle": "test_local_handle",
        "display_name": "Test Display Name",
        "discord_handle": None,
        "github_account": None,
        "discourse_account": None,
        "wiki_account": None,
        "website": None,
        "extra_info": None,
        "contributions": [],
    }

    # verify that the contributor was created in the database
    response = client.get(f"/contributors/{contributor_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contributor_id,
        "local_handle": "test_local_handle",
        "display_name": "Test Display Name",
        "discord_handle": None,
        "github_account": None,
        "discourse_account": None,
        "wiki_account": None,
        "website": None,
        "extra_info": None,
        "created_at": created_at,
        "updated_at": updated_at,
        "contributions": [],
        "reviewed_contributions": [],
    }

    # update the contributor
    response = client.put(
        f"/contributors/{contributor_id}",
        json={
            "local_handle": "test_local_handle",
            "display_name": "Updated Display Name",
        },
    )
    assert response.status_code == 200
    new_content = response.json()
    new_updated_at = new_content.pop("updated_at")
    assert new_content == {
        "id": contributor_id,
        "local_handle": "test_local_handle",
        "display_name": "Updated Display Name",
        "discord_handle": None,
        "github_account": None,
        "discourse_account": None,
        "wiki_account": None,
        "website": None,
        "extra_info": None,
        "created_at": created_at,
        "contributions": [],
    }
    assert datetime.fromisoformat(new_updated_at) > datetime.fromisoformat(updated_at)

    # verify that the contributor was updated in the database
    response = client.get(f"/contributors/{contributor_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contributor_id,
        "local_handle": "test_local_handle",
        "display_name": "Updated Display Name",
        "discord_handle": None,
        "github_account": None,
        "discourse_account": None,
        "wiki_account": None,
        "website": None,
        "extra_info": None,
        "created_at": created_at,
        "updated_at": new_updated_at,
        "contributions": [],
        "reviewed_contributions": [],
    }


def test_contributor_already_exists(client):
    # create a new contributor
    response = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle_duplicate",
            "display_name": "Test Display Name",
        },
    )
    assert response.status_code == 200, response.json()

    # try to create a contributor with the same local handle
    response = client.post(
        "/contributors/",
        json={"local_handle": "test_local_handle_duplicate"},
    )
    assert response.status_code == 417
    assert response.json() == {"detail": "Local handle already exists"}

    # try to create a contributor with the same display name
    response = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle_duplicate_2",
            "display_name": "Test Display Name",
        },
    )
    assert response.status_code == 417
    assert response.json() == {"detail": "Display name already exists"}

    # try to create a contributor with local_handle existing as display_name
    response = client.post(
        "/contributors/",
        json={"local_handle": "Test Display Name"},
    )
    assert response.status_code == 417
    assert response.json() == {"detail": "Local handle already used as display name"}

    # try to create a contributor with display_name existing as local_handle
    response = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle_duplicate_3",
            "display_name": "test_local_handle_duplicate",
        },
    )
    assert response.status_code == 417
    assert response.json() == {"detail": "Display name already used as local handle"}


def test_read_contributors(client):
    # create a two contributors
    response_1 = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle_multiple",
            "display_name": "Test Display Name Multiple",
        },
    )
    assert response_1.status_code == 200
    response_2 = client.post(
        "/contributors/",
        json={
            "local_handle": "test_local_handle_multiple_2",
            "display_name": "Test Display Name Multiple 2",
        },
    )
    assert response_2.status_code == 200

    # read the contributors
    response = client.get("/contributors/")
    all_users = response.json()
    assert response.status_code == 200
    assert len(all_users) >= 2
    for item in all_users:
        assert "local_handle" in item


def test_read_contributor_reviewed_contributions(client, add_review):
    review, contribution_1, contribution_2, contributor, _ = add_review

    # read the contributor
    response = client.get(f"/contributors/{contributor.id}/reviewed_contributions")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    assert "reviewed_contributions" in content
    assert len(content["reviewed_contributions"]) == 1
    assert content["reviewed_contributions"][0] == {
        "id": contribution_2.id,
        "title": contribution_2.title,
        "short_title": contribution_2.short_title,
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "archived_at": None,
        "archive_reason": None,
        "date": contribution_2.date.isoformat(),
        "tags": [],
        "contributors": [
            {
                "id": contributor.id,
                "local_handle": contributor.local_handle,
                "display_name": contributor.display_name,
            }
        ],
        "reviews": [{"id": review.id}],
        "dependencies": [
            {
                "id": contribution_1.id,
                "short_title": contribution_1.short_title,
                "title": contribution_1.title,
            }
        ],
    }
