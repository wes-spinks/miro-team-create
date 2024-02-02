#!/usr/bin/env python3

import json
import logging

import pytest

import app

headers = {"Content-Type": "application/json"}


def test_health(client):
    """test _health returns OK"""
    res = client.get("/_health")
    assert res.status_code == 200
    expected = "OK"
    assert expected == res.get_data(as_text=True)


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "<h1 style='color: red;'>Welcome" in res.text


def test_missing_args(client):
    missing_ticket = {
        "user": "test@domain.com",
        "team": "test team name",
        "internal": True,
    }
    output = client.post("/miro_team/create", json=missing_ticket)
    assert output.json["message"] == "Missing required argument(s): {'ticket'}"
