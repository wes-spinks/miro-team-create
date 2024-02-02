import json
import logging
import os
import pytest

from pathlib import Path
from sys import stdout
from unittest.mock import patch

TESTS_DIR = Path(__file__).parent.absolute()
mp = pytest.MonkeyPatch()

mp.syspath_prepend(str(Path(__file__).parent.parent.absolute()))

# Add any required startup environment values here
# Do so by using mp.setenv; i.e. mp.setenv("FLASK_ENV", "development")
mp.setenv("IS_TESTING", "true")
mp.setenv("MIRO_CLIENT_ID", "value")
mp.setenv("MIRO_CLIENT_SECRET", "value")

# OR add your key:values to resources/testenv.json
# Load resources/testenv.json into testing environment
with open(f"{TESTS_DIR}/resources/testenv.json", "r") as f:
    testenv = json.load(f)
    for k, v in testenv.items():
        mp.setenv(k, v)

logging.basicConfig(stream=stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

import miro_team
from app import app as flask_app  # pylint: disable=C0413


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_list_teams_no_cursor_json():
    """returns example JSON of successful GET
    /v2/orgs/{org_id}/teams?name=TEAM%20NAME"""
    with open(
        os.path.join(TESTS_DIR, "resources/miro_list_teams_no_cursor_response.json")
    ) as f:
        return json.load(f)


@pytest.fixture
def sample_notfound_json():
    """returns example JSON of error, 404 NOT FOUND response"""
    with open(os.path.join(TESTS_DIR, "resources/miro_not_found_response.json")) as f:
        return json.load(f)


@pytest.fixture
def sample_too_many_requests_json():
    """returns example JSON of error, rate limited 429 response"""
    with open(os.path.join(TESTS_DIR, "resources/miro_429_response.json")) as f:
        return json.load(f)


@pytest.fixture
def sample_get_team_settings_json():
    """returns example JSON of successful team settings GET response"""
    with open(os.path.join(TESTS_DIR, "resources/miro_get_team_settings.json")) as f:
        return json.load(f)


@pytest.fixture
def sample_patch_team_settings_json():
    """returns example JSON of successful team settings PATCH response"""
    with open(os.path.join(TESTS_DIR, "resources/miro_patch_team_settings.json")) as f:
        return json.load(f)


@pytest.fixture
def sample_team_create_response_json():
    """returns example successful team creation response"""
    with open(
        os.path.join(TESTS_DIR, "resources/miro_create_team_success_response.json")
    ) as f:
        return json.load(f)


@pytest.fixture
def patched__miro_requests(
    mocker,
    monkeypatch,
    sample_list_teams_json,
    sample_team_create_response_json,
    sample_patch_team_settings_json,
):
    """patch requests post for Miro during tests

    currently patching all PATCH, GET, and POST with the same mock
    """

    def _mresp(retdata: dict, retcode: int = 200):
        mock_resp = mocker.Mock()
        mock_resp.status_code = retcode
        mock_resp.text = json.loads(retdata)
        mock_resp.json.return_value = retdata
        return mock_resp

    def mock_post(data):
        return _mresp(sample_team_create_response_json)

    def mock_patch(data):
        return _mresp(sample_patch_team_settings_json)

    def mock_get(data):
        return _mresp(sample_list_teams_json)

    def mock_delete(data):
        return _mresp("{}", 204)

    monkeypatch.setattr(miro_team.requests, "post", mock_post)
    monkeypatch.setattr(miro_team.requests, "patch", mock_patch)
    monkeypatch.setattr(miro_team.requests, "get", mock_get)
    monkeypatch.setattr(miro_team.requests, "delete", mock_delete)
