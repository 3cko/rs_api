#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

import json
import requests


class RsAPI(object):

    def __init__(self):
        self.token_id = None
        self.tenant_id = None
        self.available_os = {}
        self.available_sizes = {}

    def getAuthentication(self, user_name, api_key):
        """
        Get Authenticated with Rackspace so you can use the API.
        """
        auth_url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
        data = {"auth":{"RAX-KSKEY:apiKeyCredentials":{"username":user_name, "apiKey":api_key}}}
        headers = {'Content-type': 'application/json'}
        request_auth = requests.post(auth_url, data=json.dumps(data), headers=headers)
        authenticated_data = request_auth.json()

        """
        token_id = authenticated_data['access']['token']['id']
        tenant_id = authenticated_data['access']['token']['tenant']['id']
        for lists in authenticated_data['access']:
            for dicts in authenticated_data['access'][lists]:
                if isinstance(dicts, dict):
                    print dicts
                    print "\n"
        """

        token_id = authenticated_data['access']['token']['id']
        tenant_id = authenticated_data['access']['token']['tenant']['id']

        self.token_id = token_id
        self.tenant_id = tenant_id

    def getOperatingSystems(self):
        os_url = "https://dfw.servers.api.rackspacecloud.com/v2/" + self.tenant_id + "/images/detail"
        os_headers = {"X-Auth-Token": str(self.token_id)}
        request_os = requests.get(os_url, headers=os_headers)

        returned_data = request_os.json()

        return returned_data

    def getServerSizes(self):
        sizes_url = "https://dfw.servers.api.rackspacecloud.com/v2/" + self.tenant_id + "/flavors"
        sizes_headers = {"X-Auth-Token": str(self.token_id)}
        request_sizes = requests.get(sizes_url, headers=sizes_headers)

        returned_data = request_sizes.json()

        return returned_data

    def getCurrentServers(self):
        current_url = "https://dfw.servers.api.rackspacecloud.com/v2/" + self.tenant_id + "/servers/detail"
        current_headers = {"X-Auth-Token": str(self.token_id)}
        request_current = requests.get(current_url, headers=current_headers)

        returned_data = request_current.json()

        return returned_data

    def getCloudFilesContainers(self):
        tenant_id = 'MossoCloudFS_b151b4a5-26c0-41ed-8e48-abec10814e8f'
        containers_url = "https://storage101.dfw1.clouddrive.com/v1/" + tenant_id + "?format=json"
        containers_headers = {"X-Auth-Token": str(self.token_id)}
        containers_data = {"content"}
        request_containers = requests.get(containers_url, headers=containers_headers)

        returned_data = request_containers.json()

        return returned_data

    def createStaticPage(self):
        static_url = "https://storage.clouddrive.com/v1/CF_xer7_343"
        #static_url = "https://cdn.clouddrive.com/v1/" + self.tenant_id + "/test?format=json"
        #static_url = "https://storage101.lon3.clouddrive.com/v1/MossoCloudFS_5b152ce0-9bbe-4c17-b5f1-4255b8766a95/drg/"
        #static_headers = {"X-Container-Meta-Web-Index": "index.html", "X-Auth-Token": str(self.token_id)}
        static_headers = {"X-Auth-Token": str(self.token_id)}
        request_static = requests.head(static_url, headers=static_headers)

        print request_static
        returned_data = request_static.json()
        return returned_data

    def createServer(self, server_name, image_ref, flavor_ref):
        my_server_name = server_name.replace(" ", "_").lower()
        create_server_url = "https://dfw.servers.api.rackspacecloud.com/v2/" + self.tenant_id + "/servers"
        data = {"server":{
                    "name": server_name,
                    "imageRef": image_ref,
                    "flavorRef": flavor_ref,
                    "OS-DCF:diskConfig": "AUTO",
                    "metadata": {
                        "My Server Name": my_server_name
                                },
                    "personality":[{
                        "path": "/etc/banner.txt",
                        "contents" : "ICAgICAgDQoiQSBjbG91ZCBkb2VzIG5vdCBrbm93IHdoeSBp\
                                    dCBtb3ZlcyBpbiBqdXN0IHN1Y2ggYSBkaXJlY3Rpb24gYW5k\
                                    IGF0IHN1Y2ggYSBzcGVlZC4uLkl0IGZlZWxzIGFuIGltcHVs\
                                    c2lvbi4uLnRoaXMgaXMgdGhlIHBsYWNlIHRvIGdvIG5vdy4g\
                                    QnV0IHRoZSBza3kga25vd3MgdGhlIHJlYXNvbnMgYW5kIHRo\
                                    ZSBwYXR0ZXJucyBiZWhpbmQgYWxsIGNsb3VkcywgYW5kIHlv\
                                    dSB3aWxsIGtub3csIHRvbywgd2hlbiB5b3UgbGlmdCB5b3Vy\
                                    c2VsZiBoaWdoIGVub3VnaCB0byBzZWUgYmV5b25kIGhvcml6\
                                    b25zLiINCg0KLVJpY2hhcmQgQmFjaA=="
                                  }],
                        "networks": [
                            {
                                "uuid": "00000000-0000-0000-0000-000000000000"
                            },
                            {
                                "uuid": "11111111-1111-1111-1111-111111111111"
                            },
                        ]
                    }
               }

        create_server_headers = {"X-Auth-Token": str(self.token_id), 'Content-type': 'application/json'}

        request_create = requests.post(create_server_url, data=json.dumps(data), headers=create_server_headers)

        returned_data = request_create.json()
        return returned_data

    def buildDict(self, returned_data):
        build = {}
        for key, value in returned_data.items():
            for data in returned_data[key]:
                build[data['name']] = data['id']
        return build

    def run(self):
        self.getAuthentication("user", "api_key")
        print self.tenant_id
        #self.available_os = self.buildDict(self.getOperatingSystems())
        #self.available_sizes = self.buildDict(self.getServerSizes())
        #print self.available_os
        #print self.available_sizes
        print self.createStaticPage()


if __name__ == '__main__':
    rs_api = RsAPI()
    rs_api.run()
