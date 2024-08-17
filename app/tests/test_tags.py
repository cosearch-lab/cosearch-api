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


def test_read_tag_with_contributions(client, add_contribution_with_tag):
    tag, contribution, contributor = add_contribution_with_tag

    # read the tag
    response = client.get(f"/tags/{tag.id}")
    assert response.status_code == 200
    content = response.json()
    del content["created_at"]
    del content["updated_at"]
    del content["contributions"][0]["tags"][0]["created_at"]
    del content["contributions"][0]["tags"][0]["updated_at"]
    assert content == {
        "id": tag.id,
        "display_name": tag.display_name,
        "color": tag.color,
        "contributions": [
            {
                "id": contribution.id,
                "title": "Test Contribution",
                "short_title": None,
                "date": "2021-01-01T00:00:00",
                "discord_chat_link": None,
                "github_link": None,
                "forum_link": None,
                "wiki_link": None,
                "highlighted_discord_message": None,
                "archived_at": None,
                "archive_reason": None,
                "contributors": [
                    {
                        "id": contributor.id,
                        "local_handle": contributor.local_handle,
                        "display_name": contributor.display_name,
                    }
                ],
                "tags": [
                    {
                        "id": tag.id,
                        "display_name": tag.display_name,
                        "color": tag.color,
                    }
                ],
                "reviews": [],
                "dependencies": [],
            }
        ],
    }
