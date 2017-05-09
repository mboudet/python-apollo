import argparse
import collections
import json
import logging
import os

from cachetools import TTLCache
from apollo.util import AssertUser
from apollo.exceptions import UnknownUserException

from apollo.client.annotations import AnnotationsClient
from apollo.client.cannedcomments import CannedCommentsClient
from apollo.client.cannedkeys import CannedKeysClient
from apollo.client.cannedvalues import CannedValuesClient
from apollo.client.groups import GroupsClient
from apollo.client.io import IOClient
from apollo.client.metrics import MetricsClient
from apollo.client.organisms import OrganismsClient
from apollo.client.status import StatusClient
from apollo.client.users import UsersClient

import requests
logging.getLogger("requests").setLevel(logging.CRITICAL)
log = logging.getLogger()


cache = TTLCache(
    100,  # Up to 100 items
    5 * 60  # 5 minute cache life
)
userCache = TTLCache(
    10,  # Up to 2 items
    60  # 1 minute cache life
)


class WebApolloInstance(object):

    def __init__(self, url, username, password):
        self.apollo_url = url
        self.username = username
        self.password = password

        self.annotations = AnnotationsClient(self)
        self.groups = GroupsClient(self)
        self.io = IOClient(self)
        self.organisms = OrganismsClient(self)
        self.users = UsersClient(self)
        self.metrics = MetricsClient(self)
        self.status = StatusClient(self)
        self.canned_comments = CannedCommentsClient(self)
        self.canned_keys = CannedKeysClient(self)
        self.canned_values = CannedValuesClient(self)

    def __str__(self):
        return '<WebApolloInstance at %s>' % self.apollo_url

    def require_user(self, email):
        """Require that the user has an account"""
        cache_key = 'user-list'
        try:
            # Get the cached value
            data = userCache[cache_key]
        except KeyError:
            # If we hit a key error above, indicating that
            # we couldn't find the key, we'll simply re-request
            # the data
            data = self.users.loadUsers()
            userCache[cache_key] = data

        return AssertUser([x for x in data if x.username == email])


def accessible_organisms(user, orgs):
    """Get the list of organisms accessible to a user, filtered by `orgs`"""
    permission_map = {
        x['organism']: x['permissions']
        for x in user.organismPermissions
        if 'WRITE' in x['permissions'] or
        'READ' in x['permissions'] or
        'ADMINISTRATE' in x['permissions'] or
        user.role == 'ADMIN'
    }

    if 'error' in orgs:
        raise Exception("Error received from Apollo server: \"%s\"" % orgs['error'])

    return [
        (org['commonName'], org['id'], False)
        for org in sorted(orgs, key=lambda x: x['commonName'])
        if org['commonName'] in permission_map
    ]


def galaxy_list_groups(trans, *args, **kwargs):
    email = trans.get_user().email
    wa = WebApolloInstance(
        os.environ['GALAXY_WEBAPOLLO_URL'],
        os.environ['GALAXY_WEBAPOLLO_USER'],
        os.environ['GALAXY_WEBAPOLLO_PASSWORD']
    )
    # Assert that the email exists in apollo
    try:
        gx_user = wa.requireUser(email)
    except UnknownUserException:
        return []

    # Key for cached data
    cacheKey = 'groups-' + email
    # We don't want to trust "if key in cache" because between asking and fetch
    # it might through key error.
    if cacheKey not in cache:
        # However if it ISN'T there, we know we're safe to fetch + put in
        # there.
        data = _galaxy_list_groups(wa, gx_user, *args, **kwargs)
        cache[cacheKey] = data
        return data
    try:
        # The cache key may or may not be in the cache at this point, it
        # /likely/ is. However we take no chances that it wasn't evicted between
        # when we checked above and now, so we reference the object from the
        # cache in preparation to return.
        data = cache[cacheKey]
        return data
    except KeyError:
        # If access fails due to eviction, we will fail over and can ensure that
        # data is inserted.
        data = _galaxy_list_groups(wa, gx_user, *args, **kwargs)
        cache[cacheKey] = data
        return data


def _galaxy_list_groups(wa, gx_user, *args, **kwargs):
    # Fetch the groups.
    group_data = []
    for group in wa.groups.loadGroups():
        # Reformat
        group_data.append((group.name, group.groupId, False))
    return group_data


def galaxy_list_orgs(trans, *args, **kwargs):
    email = trans.get_user().email
    wa = WebApolloInstance(
        os.environ['GALAXY_WEBAPOLLO_URL'],
        os.environ['GALAXY_WEBAPOLLO_USER'],
        os.environ['GALAXY_WEBAPOLLO_PASSWORD']
    )
    try:
        gx_user = wa.requireUser(email)
    except UnknownUserException:
        return []

    # Key for cached data
    cacheKey = 'orgs-' + email
    if cacheKey not in cache:
        data = _galaxy_list_orgs(wa, gx_user, *args, **kwargs)
        cache[cacheKey] = data
        return data
    try:
        data = cache[cacheKey]
        return data
    except KeyError:
        data = _galaxy_list_orgs(wa, gx_user, *args, **kwargs)
        cache[cacheKey] = data
        return data


def _galaxy_list_orgs(wa, gx_user, *args, **kwargs):
    # Fetch all organisms
    all_orgs = wa.organisms.findAllOrganisms()
    # Figure out which are accessible to the user
    orgs = accessible_organisms(gx_user, all_orgs)
    # Return org list
    return orgs


# This is all for implementing the command line interface for testing.
class obj(object):
    pass


class fakeTrans(object):

    def __init__(self, username):
        self.un = username

    def get_user(self):
        o = obj()
        o.email = self.un
        return o


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test access to apollo server')
    parser.add_argument('email', help='Email of user to test')
    parser.add_argument('--action', choices=['org', 'group'], default='org', help='Data set to test, fetch a list of groups or users known to the requesting user.')
    args = parser.parse_args()

    trans = fakeTrans(args.email)
    if args.action == 'org':
        for f in galaxy_list_orgs(trans):
            print(f)
    else:
        for f in galaxy_list_groups(trans):
            print(f)
