#!/usr/bin/env python3

import json

import miro_team

headers = {"Content-Type": "application/json"}


def test_all_teams(mocker, sample_list_teams_no_cursor_json):
    mresp = mocker.Mock()
    mresp.json.return_value = sample_list_teams_no_cursor_json
    mresp.raise_for_status.return_value = None
    mocker.patch("miro_team.requests.get", return_value=mresp)
    outlist = miro_team.all_teams()
    assert len(outlist) == 2
    assert outlist == ["Enterprise Sandbox", "team1"]
