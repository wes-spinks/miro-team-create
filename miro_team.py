import logging
import os
import requests
import time

from requests.exceptions import HTTPError, ConnectionError

from team_configs import INT_TEAM_SETTINGS, EXT_TEAM_SETTINGS

log = logging.getLogger(__name__)

ORG_ID = os.environ.get("ORG_ID", "3458764577187960805")
MIRO_BASE = f"https://api.miro.com/v2/orgs/{ORG_ID}"
MIRO_HEADER = {
    "Authorization": f"Bearer {os.environ.get('MIRO_REST_TOKEN')}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
# Need our service account ID to remove it later
MIRO_SA_ID = os.environ.get("MIRO_SA_ID", "3074457353710057935")


def __transport_req(req: requests.Request) -> dict:
    """Snagged this from RC heh...
    uses internal opener/session to make request and handle error logging

    Arguments:
        req {request.Request} -- HTTP request to prepare and send

    Raises:
        ResponseError: On http errors (return codes that are not "OK")

    Returns:
        dict -- response object from API's json request
    """
    retry_call = 0
    open_session = requests.Session()
    while retry_call < 1:
        try:
            rresp = open_session.send(req.prepare())
            rresp.raise_for_status()
        except HTTPError as err:
            log.error(err.response.text)
            if err.response.status_code == 429:
                log.debug(
                    "Rate limit hit, pausing for 60 seconds",
                )
                time.sleep(60)
                retry_call = -1
            else:
                raise HTTPError(
                    err.response.status_code,
                    err.response.reason,
                    err.response.json()["message"],
                ) from err
        try:
            if int(rresp.headers["X-RateLimit-Remaining"]) <= 10000:
                log.debug("Nearing limit, pausing for 30 seconds")
                time.sleep(30)
        except KeyError:
            pass
        retry_call += 1
    try:
        return rresp.json()
    except requests.exceptions.JSONDecodeError as err:
        if not rresp.content:
            return {}
        raise
        # raise JsonDecodeError(msg=rresp.body) from err


def all_teams(limit: int = 100) -> list:
    """Get a list of all team names in given org

    Returns:
        list: all team names in ORG_ID
    """
    teams = []
    url = f"{MIRO_BASE}/teams?limit={limit}"
    try:
        resp = requests.get(url, headers=MIRO_HEADER)
        resp.raise_for_status()
        rjson = resp.json()
        teams += rjson["data"]
        cursor = rjson.get("cursor")
        while cursor is not None:
            log.debug("in while")
            params = {"cursor": cursor}
            response = requests.get(url, params=params, headers=MIRO_HEADER)
            response.raise_for_status()
            resp = response.json()
            if resp["size"] > 0:
                teams += resp["data"]
                cursor = resp["cursor"]
            else:
                cursor = None
    except (HTTPError, ConnectionError) as exce:
        log.info(exce.response.text)
        log.error("Failed to collect teams list: %s", exce)
    finally:
        return [team.get("name") for team in teams if team.get("type") == "team"]


def create(teamname: str) -> dict:
    """Create a team, regardless of existence.
    Return dict about new team
    to use in follow up calls to configure, or empty dict

    Arguments:
        teamname (str): confirmed non-existent requested team name

    Returns:
        dict: with new team data, mainly the ID. or an empty dict

    Raises:
        HTTPError: request issue
        ConnectionError: request issue
    """
    endpoint = f"{MIRO_BASE}/teams"
    payload = {"name": "{}".format(teamname)}
    print(payload)
    req = requests.Request(
        method="POST", url=endpoint, headers=MIRO_HEADER, json=payload
    )
    return __transport_req(req)


def invite_requester_admin(useremail: str, team_id: str) -> dict:
    """POST to invite requester to team as admin
    # payload = {"role": "admin","email": "requester@domain.com"}
    # https://developers.miro.com/reference/enterprise-invite-team-member

    Arguments:
        useremail (str): email of requesting user
        team_id (str): ID of created team

    Returns:
        dict: containing user membership details

    Raises:
        HTTPError: request issue
        ConnectionError: request issue
    """
    endpoint = f"{MIRO_BASE}/teams/{team_id}/members"
    payload = {"role": "admin", "email": useremail}
    req = requests.Request(
        method="POST", url=endpoint, headers=MIRO_HEADER, json=payload
    )
    return __transport_req(req)


def delete_user(user_id: str, team_id: str) -> dict:
    """Remove user from team.
    Mainly to remove the service account used to create

    Arguments:
        user_id (str): unique user ID
        team_id (str): unique ID of team to remove user from

    Raises:
        HTTPError: request/response issue
        ConnectionError: network issue
    """
    endpoint = f"{MIRO_BASE}/teams/{team_id}/members/{user_id}"
    req = requests.Request(
        method="DELETE",
        url=endpoint,
        headers=MIRO_HEADER,
    )
    return __transport_req(req)


def apply_settings(team_id: str, is_internal: bool) -> dict:
    """PATCH team settings to set internal teams restricted domains
    { "teamSharingPolicySettings": { "restrictAllowedDomains": "enabled" } }

    Arguments:
        team_id (int): integer ID of the new internal team
        is_internal (bool): True if internal team request

    Returns:
        dict: dictionary containing updated team setting values, or empty dict
    """
    endpoint = f"{MIRO_BASE}/teams/{team_id}/settings"
    if is_internal:
        payload = INT_TEAM_SETTINGS()
    else:
        payload = EXT_TEAM_SETTINGS()
    req = requests.Request(
        method="PATCH", url=endpoint, headers=MIRO_HEADER, json=payload
    )
    return __transport_req(req)


def process_team_request(data: dict) -> dict:
    """main function. checks for existence before creating
    team, updating team image, settings, and team membership

    attempts to create an existing team will create a duplicate

    takes dict of at least MANDATORY_ARGS from app.py
    and returns a dict with at least message and status

    intended to replace:
    https://gitlab.corp.redhat.com/rpa/it/miro_team_creation/it_gs_miroteamcreation_performer/-/blob/release/Process.xaml
    https://docs.google.com/document/d/1eaJB6XUNB-CHst2x0hEdcWmP4JN1HBgi11R08LTJdYU/edit

    response{json}:
        Status[str]:
            one of the following states: "Success" "Failed"  "Error" "Exception"
        Message[str]:allowed_exception
            Information to the user about the endpoint action
    """
    response = {"message": "Default failure msg", "status": "Failed"}
    current_teams_list = all_teams()

    is_internal = data.get("internal")
    if is_internal:
        new_name = "Internal - " + data["team"]
    else:
        new_name = "External - " + data["team"]
    if any(name in current_teams_list for name in (data["team"], new_name)):
        response = {"message": "{} exists".format(data["team"]), "status": "Success"}
        return response
    log.debug("{} does not exist, proceeding...".format(new_name))
    # if it doesn't exist, create then configure
    create_resp = create(new_name)
    if not create_resp.get("id"):
        response["message"] = "Unable to identify ID of team."
        return response
    new_team_id = create_resp["id"]
    # Apply settings, either internal or external settings
    settings_resp = apply_settings(new_team_id, is_internal)
    team_url = "https://miro.com/app/settings/team/{}/profile".format(new_team_id)
    if (
        not settings_resp["teamAccountDiscoverySettings"].get("accountDiscovery")
        == "hidden"
    ):
        response[
            "message"
        ] = "Created team, but settings may be incorrect. Review: {}".format(team_url)
        return response
    # TEAM PICTURE API WAS DEPRECATED
    # https://developers.miro.com/v1.0/reference/create-or-update-picture
    # update_team_image(new_id, is_internal)
    if invite_requester_admin(data["user"], new_team_id):
        delete_user(MIRO_SA_ID, new_team_id)
    return {
        "message": "Created '{}' with admin '{}'. URL: {}".format(
            new_name, data["user"], team_url
        ),
        "status": "Success",
    }
