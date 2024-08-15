from datetime import datetime


def test_create_review(client, add_contribution):
    contribution, contributor_1, contributor_2 = add_contribution

    response = client.post(
        "/reviews",
        json={
            "contribution_id": contribution.id,
            "reviewers": [contributor_1.id],
            "link": "https://example.com/",
            "notes": "Test notes",
        },
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    created_at = content.pop("created_at")
    updated_at = content.pop("updated_at")
    review_id = content.pop("id")
    assert content == {
        "contribution_id": contribution.id,
        "link": "https://example.com/",
        "notes": "Test notes",
        "reviewers": [
            {
                "id": contributor_1.id,
                "local_handle": "test_contributor",
                "display_name": "Test Contributor",
            }
        ],
    }

    # verify the review was created in the database
    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "id": review_id,
        "contribution_id": contribution.id,
        "link": "https://example.com/",
        "notes": "Test notes",
        "reviewers": [
            {
                "id": contributor_1.id,
                "local_handle": "test_contributor",
                "display_name": "Test Contributor",
            }
        ],
        "created_at": created_at,
        "updated_at": updated_at,
    }

    # update the review
    response = client.put(
        f"/reviews/{review_id}",
        json={
            "contribution_id": contribution.id,
            "reviewers": [contributor_2.id],
            "link": "https://example.com/",
            "notes": "",
        },
    )
    assert response.status_code == 200, response.json()
    new_content = response.json()
    new_updated_at = new_content.pop("updated_at")
    assert new_content == {
        "id": review_id,
        "contribution_id": contribution.id,
        "link": "https://example.com/",
        "notes": None,
        "reviewers": [
            {
                "id": contributor_2.id,
                "local_handle": "test_contributor2",
                "display_name": "Test Contributor 2",
            }
        ],
        "created_at": created_at,
    }
    assert datetime.fromisoformat(new_updated_at) > datetime.fromisoformat(updated_at)

    # verify the review was updated in the database
    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 200, response.json()
    assert response.json() == {
        "id": review_id,
        "contribution_id": contribution.id,
        "link": "https://example.com/",
        "notes": None,
        "reviewers": [
            {
                "id": contributor_2.id,
                "local_handle": "test_contributor2",
                "display_name": "Test Contributor 2",
            }
        ],
        "created_at": created_at,
        "updated_at": new_updated_at,
    }


def test_read_contribution_with_review(
    client,
    add_review,
):
    review, _, contribution_2, contributor_1, _ = add_review

    response = client.get(f"/contributions/{contribution_2.id}")
    assert response.status_code == 200, response.json()
    content = response.json()
    del content["created_at"]
    del content["updated_at"]
    del content["reviews"][0]["created_at"]
    del content["reviews"][0]["updated_at"]
    del content["dependencies"]  # don't need to test this
    reviews = content.pop("reviews")
    assert content == {
        "id": contribution_2.id,
        "title": "Test Contribution 2",
        "short_title": None,
        "date": "2021-01-01T00:00:00",
        "discord_chat_link": None,
        "github_link": None,
        "forum_link": None,
        "wiki_link": None,
        "archived_at": None,
        "archive_reason": None,
        "links": [
            {
                "description": "Test link 2",
                "url": "https://example2.com/",
            }
        ],
        "description": "Test description 2",
        "contributors": [
            {
                "id": contributor_1.id,
                "local_handle": "test_contributor",
                "display_name": "Test Contributor",
            }
        ],
        "tags": [],
    }
    assert len(reviews) == 1
    assert reviews[0] == {
        "id": review.id,
        "contribution_id": contribution_2.id,
        "link": "https://example.com/",
        "notes": "Test review notes",
        "reviewers": [
            {
                "id": contributor_1.id,
                "local_handle": "test_contributor",
                "display_name": "Test Contributor",
            }
        ],
    }
