from datetime import datetime


def test_create_contribution(client, add_contributors):
    response = client.get("/contributors/")
    assert response.status_code == 200
    contributor_id = response.json()[0]["id"]
    contributor_local_handle = response.json()[0]["local_handle"]
    contributor_display_name = response.json()[0]["display_name"]

    # create a new contribution
    response = client.post(
        "/contributions/",
        json={
            "title": "Test Contribution",
            "short_title": "Test Contrib",
            "date": "2021-01-01 00:00:00",
            "discord_chat_link": "https://discord.com/chat",
            "github_link": None,
            "forum_link": "",
            "links": [
                {
                    "description": "Test Description",
                    "url": "https://example.com",
                },
            ],
            "description": "Test Description",
            "contributors": [contributor_id],
            "tags": [],
        },
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    created_at = content.pop("created_at")
    updated_at = content.pop("updated_at")
    contribution_id = content.pop("id")
    assert content == {
        "title": "Test Contribution",
        "short_title": "Test Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": "https://discord.com/chat",
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Test Description",
                "url": "https://example.com/",
            },
        ],
        "description": "Test Description",
        "archived_at": None,
        "archive_reason": None,
        "contributors": [
            {
                "id": contributor_id,
                "local_handle": contributor_local_handle,
                "display_name": contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }

    # verify that the contribution was created in the database
    response = client.get(f"/contributions/{contribution_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contribution_id,
        "title": "Test Contribution",
        "short_title": "Test Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": "https://discord.com/chat",
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Test Description",
                "url": "https://example.com/",
            },
        ],
        "description": "Test Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "updated_at": updated_at,
        "contributors": [
            {
                "id": contributor_id,
                "local_handle": contributor_local_handle,
                "display_name": contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }

    # update the contribution but without changing the contributors
    response = client.put(
        f"/contributions/{contribution_id}",
        json={
            "title": "Updated Contribution",
            "short_title": "Updated Contrib",
            "date": "2021-01-01 00:00:00",
            "discord_chat_link": "https://discord.com/chat",
            "forum_link": "",
            "wiki_link": "https://wiki.com",
            "links": [
                {
                    "description": "Updated Description",
                    "url": "https://example.com",
                },
                {
                    "description": "New Description",
                    "url": "https://example2.com",
                },
            ],
            "description": "Updated Description",
            "contributors": [contributor_id],
            "tags": [],
        },
    )
    assert response.status_code == 200
    new_content = response.json()
    new_updated_at = new_content.pop("updated_at")
    assert new_content == {
        "id": contribution_id,
        "title": "Updated Contribution",
        "short_title": "Updated Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": "https://discord.com/chat",
        "github_link": None,
        "forum_link": None,
        "wiki_link": "https://wiki.com/",
        "links": [
            {
                "description": "Updated Description",
                "url": "https://example.com/",
            },
            {
                "description": "New Description",
                "url": "https://example2.com/",
            },
        ],
        "description": "Updated Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "contributors": [
            {
                "id": contributor_id,
                "local_handle": contributor_local_handle,
                "display_name": contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }
    assert datetime.fromisoformat(new_updated_at) > datetime.fromisoformat(updated_at)

    # verify that the contribution was updated in the database
    response = client.get(f"/contributions/{contribution_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contribution_id,
        "title": "Updated Contribution",
        "short_title": "Updated Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": "https://discord.com/chat",
        "github_link": None,
        "forum_link": None,
        "wiki_link": "https://wiki.com/",
        "links": [
            {
                "description": "Updated Description",
                "url": "https://example.com/",
            },
            {
                "description": "New Description",
                "url": "https://example2.com/",
            },
        ],
        "description": "Updated Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "updated_at": new_updated_at,
        "contributors": [
            {
                "id": contributor_id,
                "local_handle": contributor_local_handle,
                "display_name": contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }


def test_update_contributors_in_contribution(client, add_contributors):
    response = client.get("/contributors/")
    assert response.status_code == 200
    first_contributor_id = response.json()[0]["id"]
    first_contributor_local_handle = response.json()[0]["local_handle"]
    first_contributor_display_name = response.json()[0]["display_name"]
    second_contributor_id = response.json()[1]["id"]
    second_contributor_local_handle = response.json()[1]["local_handle"]
    second_contributor_display_name = response.json()[1]["display_name"]

    # create a new contribution
    response = client.post(
        "/contributions/",
        json={
            "title": "Test Contribution",
            "short_title": "Test Contrib",
            "date": "2021-01-01 00:00:00",
            "links": [
                {
                    "description": "Test Description",
                    "url": "https://example.com",
                },
            ],
            "description": "Test Description",
            "contributors": [first_contributor_id],
            "tags": [],
        },
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    created_at = content.pop("created_at")
    updated_at = content.pop("updated_at")
    contribution_id = content.pop("id")
    assert content == {
        "title": "Test Contribution",
        "short_title": "Test Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Test Description",
                "url": "https://example.com/",
            },
        ],
        "description": "Test Description",
        "archived_at": None,
        "archive_reason": None,
        "contributors": [
            {
                "id": first_contributor_id,
                "local_handle": first_contributor_local_handle,
                "display_name": first_contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }

    # verify that the contribution was created in the database
    response = client.get(f"/contributions/{contribution_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contribution_id,
        "title": "Test Contribution",
        "short_title": "Test Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Test Description",
                "url": "https://example.com/",
            },
        ],
        "description": "Test Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "updated_at": updated_at,
        "contributors": [
            {
                "id": first_contributor_id,
                "local_handle": first_contributor_local_handle,
                "display_name": first_contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }

    # update the contribution by changing the contributors
    response = client.put(
        f"/contributions/{contribution_id}",
        json={
            "title": "Updated Contribution",
            "short_title": "Updated Contrib",
            "date": "2021-01-01 00:00:00",
            "links": [
                {
                    "description": "Updated Description",
                    "url": "https://example.com",
                }
            ],
            "description": "Updated Description",
            "contributors": [second_contributor_id],
            "tags": [],
        },
    )
    assert response.status_code == 200
    new_content = response.json()
    new_updated_at = new_content.pop("updated_at")
    assert new_content == {
        "id": contribution_id,
        "title": "Updated Contribution",
        "short_title": "Updated Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Updated Description",
                "url": "https://example.com/",
            }
        ],
        "description": "Updated Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "contributors": [
            {
                "id": second_contributor_id,
                "local_handle": second_contributor_local_handle,
                "display_name": second_contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }
    assert datetime.fromisoformat(new_updated_at) > datetime.fromisoformat(updated_at)

    # verify that the contribution was updated in the database
    response = client.get(f"/contributions/{contribution_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": contribution_id,
        "title": "Updated Contribution",
        "short_title": "Updated Contrib",
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "links": [
            {
                "description": "Updated Description",
                "url": "https://example.com/",
            }
        ],
        "description": "Updated Description",
        "archived_at": None,
        "archive_reason": None,
        "created_at": created_at,
        "updated_at": new_updated_at,
        "contributors": [
            {
                "id": second_contributor_id,
                "local_handle": second_contributor_local_handle,
                "display_name": second_contributor_display_name,
            }
        ],
        "tags": [],
        "reviews": [],
        "dependencies": [],
    }
