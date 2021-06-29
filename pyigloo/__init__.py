# -*- coding: utf-8 -*-
"""
pyigloo is a small wrapper for Igloo API calls in Python


.. codeauthor:: Benjamin Kahn <xkahn@redhat.com>

Usage example:
>>>

"""

class igloo:

    import requests

    IGLOO_API_ROOT_V1 = ".api/api.svc/"
    IGLOO_API_ROOT_V2 = ".api2/api/"

    ticket = None
    igloo = None
    endpoint = None

    def __init__(self, info, session=None, version=2):
        self.endpoint = info["API_ENDPOINT"]
        self.communitykey = info["COMMUNITY_KEY"]
        self.igloo = self.requests.session()
        if session == None:
            self.connect(info,version=version)
        else:
            self.adopt(session)

    def __repr__(self):
        return '<{} @ {}>'.format(self.ticket, self.endpoint)

    def connect (self, info, version=2):

        if version == 2:
            params = {
                "AppId": info["ACCESS_KEY"],
                "AppPassword": info["API_KEY"],
                "UserName": info["API_USER"],
                "UserPassword": info["API_PASSWORD"],
                "instance": 0,  # FIXME: Allow this to be set
                "version": 1  # FIXME: Allow this to be set
            }
            result = self.get_session_v2(params)
            cookie = self.requests.cookies.create_cookie("iglooauth", result.json()['TokenId'])
        else:
            params = {
                "appId": info["ACCESS_KEY"],
                "appPass": info["API_KEY"],
                "username": info["API_USER"],
                "password": info["API_PASSWORD"],
                "apiversion": 1,
                "community": info["API_ENDPOINT"]
            }
            result = self.get_session_v1(params)
            cookie = self.requests.cookies.create_cookie ("iglooauth", result.json()["response"]['sessionKey'])
        self.igloo.cookies.set_cookie(cookie)
        self.ticket = cookie

    def adopt (self, session):
        cookie = self.requests.cookies.create_cookie ("iglooauth", session)
        self.igloo.cookies.set_cookie(cookie)
        self.ticket = cookie

    def get_session_v1 (self, params):
        """
        APIv1 session/create

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Session/post__api_api_svc_session_create
        """
        url = '{0}{1}session/create'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, data=params, headers=headers)
        return result

    def get_session_v2 (self, params):
        """
        APIv2 Session/Create

        https://customercare.igloosoftware.com/cmedia/api-docs/?api=api2#/Session/Session_CreateV1
        """
        url = '{0}{1}Session/Create'.format(self.endpoint, self.IGLOO_API_ROOT_V2)
        result = self.igloo.post(url, json=params)
        return result

    def get_web_uri (self, url):
        """
        Using the login key, pull and return a full igloo web page instead of an API call

        url: The URL fragment (not including ENDPOINT) to retrieve
        returns: The full requests response object
        """
        url = '{0}{1}'.format(self.endpoint, url)
        result = self.igloo.get(url)
        return result

    def community_view (self):
        """ 
        APIv1 community/view call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Community/get__api_api_svc_community_view
        """
        url = '{0}{1}community/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def community_info (self):
        """
        APIv2 community/info call

        https://customercare.igloosoftware.com/cmedia/api-docs/?api=api2#/Community/Community_GetCommunityInfoByDomain
        """
        url = '{0}{1}/community/info'.format(self.endpoint, self.IGLOO_API_ROOT_V2)
        result = self.igloo.post(url)
        return result

    def objects_bypath (self, path, domain = None):
        """
        APIv1 objects/byPath call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Objects/get__api_api_svc_objects_byPath
        Given a URI fragment, return information about the object

        This is the most common API call, allowing you to dereference a URL to an ID
        """
        url = '{0}{1}/objects/byPath'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers, params={'path': path, 'domain': domain})
        return result.json()['response']

    def apisync_view_usergroups (self, userIds = []):
        """
        APIv1 apisync/view_usergroups call
        
        https://customercare.igloosoftware.com/cmedia/api-docs/#/APISync/post__api_api_svc_apisync_view_usergroups
        Return a list of group IDs a user belongs to
        """
        url = '{0}{1}/apisync/view_usergroups'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        payload = {"userIds": userIds}
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers, params=payload)
        return result.json()['dictionary']

    def community_usergroups_view (self, usergroupId):
        """
        APIv1 /community/usergroups/{usergroupId}/view call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/CommunityUserGroups/get__api_api_svc_community_usergroups__usergroupId__view
        """
        url = '{0}{1}/community/usergroups/{2}/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, usergroupId)
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def get_children_of_folder (self, folderid):
        """
        APIv1
        Gets the children of the folder.

        Given an ID of the folder, returns all of its children

        """
        url = '{0}{1}/folders/{2}/children/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, folderid)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def move(self, id, destination, domain=None):
        """
        Move an object by id to a destination channel - also by id.
        Destination channel MUST be of the same type as the object.
        """
        url = '{0}{1}/objects/{2}/move?destination={3}&parentId={4}'.format(self.endpoint, self.IGLOO_API_ROOT_V1, id, destination, destination)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']

    def search(self, offset, limit, query=""):
        """
        Searches for content
        :return: Search results - JSON Format
        """
        url = '{0}{1}/communities/{2}/search/content?query=\"{3}\"&limit={4}&offset={5}&applications=Document'.format(self.endpoint, self.IGLOO_API_ROOT_V2, self.communitykey, query, limit, offset)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def create_label_group(self, labelgroupname):
        """
        Creates new label group
        :return: New label group ID - JSON Format
        """
        url = '{0}{1}/categories/classes/add?name={2}'.format(self.endpoint, self.IGLOO_API_ROOT_V1, labelgroupname)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def delete_label_group(self, labelgroup_id, keeplabels=False):
        """
        Deletes label group by id
        """
        _keep = 'false'

        if keeplabels:
            _keep = 'true'
            url = '{0}{1}/categories/classes/{2}/delete?keepCategories={3}'.format(self.endpoint, self.IGLOO_API_ROOT_V1, labelgroup_id,
                                                                                          _keep)
        else:
            url = '{0}{1}/categories/classes/{2}/delete?keepCategories={3}'.format(self.endpoint, self.IGLOO_API_ROOT_V1,
                                                                                 labelgroup_id,
                                                                                 _keep)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def create_label(self, label, group=None):
        """
        Creates new label (within a label group or on its own)
        :return: New label ID - JSON Format
        """
        if group != None:
            url = "{0}{1}/categories/add?name={2}&categoryClassId={3}".format(self.endpoint, self.IGLOO_API_ROOT_V1, label, group)
        else:
            url = "{0}{1}categories/add?name={2}".format(self.endpoint, self.IGLOO_API_ROOT_V1, label)

        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def delete_label(self, label_id):
        """
        Deletes label by id
        """
        url = "{0}{1}/categories/{2}/delete".format(self.endpoint, self.IGLOO_API_ROOT_V1, label_id)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def view_labels_in_group(self, labelgroup_id):
        """
        Views all labels for given label group ID
        :return: All labels within the label group specified - JSON Format
        """
        url = "{0}{1}/categories/classes/{2}/viewCategories".format(self.endpoint, self.IGLOO_API_ROOT_V1, labelgroup_id)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']


    def add_label_to_object(self, object_id, label_id):
        """
        Associates the given label with the specified object
        """
        url = "{0}{1}/objects/{2}/add_categories?categories={3}".format(self.endpoint, self.IGLOO_API_ROOT_V1, object_id, label_id)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def remove_label_from_object(self, object_id, label_id):
        """
        Disassociates the given label with the specified object
        """
        url = "{0}{1}/objects/{2}/remove_categories?categories={3}".format(self.endpoint, self.IGLOO_API_ROOT_V1, object_id, label_id)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers)
        return result.json()['response']


    def search_content_by_label(self, query):
        """
        Searches for content with the given label name
        :return: List of all objects that are associated with the specified label - JSON Format
        """
        url = "{0}{1}/communities/{2}/search/content?query={3}&objectSearchType=Labels".format(self.endpoint, self.IGLOO_API_ROOT_V2,
                                                                                                      self.communitykey,
                                                                                                      query)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']
