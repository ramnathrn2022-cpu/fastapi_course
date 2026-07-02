import pytest
from app import models

@pytest.fixture()
def test_vote(session, test_posts, test_user):
    new_vote = models.Vote(post_id=test_posts[2].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 201
    assert res.json() == {"message": "successfully added vote"}

def test_vote_already_voted(authorized_client, test_posts, test_vote):
    # test_posts[2] already has a vote from test_user
    res = authorized_client.post("/vote/", json={"post_id": test_posts[2].id, "dir": 1})
    assert res.status_code == 409

def test_delete_vote_success(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[2].id, "dir": 0})
    assert res.status_code == 201
    assert res.json() == {"message": "successfully deleted vote"}

def test_delete_vote_not_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 0})
    assert res.status_code == 404

def test_vote_post_not_exist(authorized_client):
    res = authorized_client.post("/vote/", json={"post_id": 9999, "dir": 1})
    assert res.status_code == 404

def test_unauthorized_user_vote(client, test_posts):
    res = client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 401
