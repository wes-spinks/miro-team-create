def INT_TEAM_SETTINGS() -> dict:
    return {
        "teamAccountDiscoverySettings": {"accountDiscovery": "hidden"},
        "teamCopyAccessLevelSettings": {
            "copyAccessLevel": "team_editors",
            "copyAccessLevelLimitation": "anyone",
        },
        "teamInvitationSettings": {
            "whoCanInvite": "all_members",
            "inviteExternalUsers": "allowed",
        },
        "teamSharingPolicySettings": {
            "createAssetAccessLevel": "all_members",
            "defaultBoardAccess": "edit",
            "defaultOrganizationAccess": "private",
            "defaultProjectAccess": "view",
            "moveBoardToAccount": "allowed",
            "restrictAllowedDomains": "enabled",
            "allowListedDomains": ["redhat.com"],
            "sharingOnAccount": "allowed",
            "sharingOnOrganization": "allowed",
            "sharingViaPublicLink": "not_allowed",
        },
    }


def EXT_TEAM_SETTINGS() -> dict:
    return {
        "teamAccountDiscoverySettings": {"accountDiscovery": "hidden"},
        "teamCopyAccessLevelSettings": {
            "copyAccessLevel": "team_editors",
            "copyAccessLevelLimitation": "anyone",
        },
        "teamInvitationSettings": {
            "whoCanInvite": "admins",
            "inviteExternalUsers": "allowed",
        },
        "teamSharingPolicySettings": {
            "createAssetAccessLevel": "all_members",
            "defaultBoardAccess": "edit",
            "defaultOrganizationAccess": "private",
            "defaultProjectAccess": "view",
            "moveBoardToAccount": "allowed",
            "restrictAllowedDomains": "disabled",
            "sharingOnAccount": "allowed",
            "sharingOnOrganization": "allowed",
            "sharingViaPublicLink": "not_allowed",
        },
    }
