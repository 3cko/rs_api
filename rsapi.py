#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

import json
import requests
from pprint import pprint


class RsAPI(object):

    def __init__(self):
        self.token_id = None
        self.tenant_id = None
        self.available_os = {}
        self.available_sizes = {}
        self.services = {}
        self.headers = {'content' : {"Content-Type": "foobar"}}
        self.get_extensions = {'getOS':'/images/detail',
                               'getSizes':'/flavors',
                               'getInstalledServers':'/servers/detail',
                               'GetCloudFilesContainers':'?format=json',
                               }

    def prettyPrint(self, json_data):
        pretty = pprint(json_data)
        return pretty

    def convertBytesToMegs(self, bytes):
        megs = float(bytes) / 1024 / 1024
        dec = "{0:.2f}".format(megs)
        return dec

    def convertToJson(self, json_data):
        raw_dump = json.dumps(json_data)
        data = json.loads(raw_dump)

        return data

    def parseJsonForOs(self, json_data):
        OS_list = []
        images = json_data['images']
        for inc, k in enumerate(images):
            for data in images[inc]:
                if "name" in data:
                    name = images[inc][data]
                if "id" in data:
                    id = images[inc][data]
            print id + ' - ' + name

    def parseCloudFiles(self, json_data):
        data = self.convertToJson(json_data)

        for row in data:
            statement = "{0:<30} {1:^1} {2:^6} Files {1:^1} {3:<6} Megs".format(\
                row['name'], '|', str(row['count']),\
                str(self.convertBytesToMegs(row['bytes'])))
            print statement

    def parseCloudFilesInContainer(self, json_data):
        data = self.convertToJson(json_data)
        li = []
        total_size = len(data)
        total_cnt = 0
        cnt = 0
        for row in data:
            total_cnt += 1
            if cnt < 3:
                li.append(row['name'])
                cnt += 1
                if len(li) == 3:
                    statement = "{1:<32} {0:^1} {2:<32} {0:^1} {3:<32}".format('|', li[0], li[1], li[2])
                    cnt = 0
                    li = []
                    print statement
                elif total_size == total_cnt and len(li) == 2:
                    statement = "{1:<32} {0:^1} {2:<32}".format('|', li[0], li[1])
                    cnt = 0
                    li = []
                    print statement
                elif total_size == total_cnt and len(li) == 1:
                    statement = "{0:<32}".format(li[0])
                    print statement

    def parseCurrentServers(self, json_data):
        data = self.convertToJson(json_data)

        for row in data['servers']:
            if 'status' in row:
                status = row['status']
            if 'name' in row:
                name = row['name']
            if 'created' in row:
                created = row['created']
            if 'accessIPv4' in row:
                ip4 = row['accessIPv4']

            statement = "{0:<50} {1: ^1} {2:^10} {1: ^2} {3:<16} {1: ^2} {4}".format(name, '|', status,
                        ip4, created)
            print statement

    def buildDictFromAuth(self, auth_data):
        data = self.convertToJson(auth_data)

        access = data['access']
        services = access['serviceCatalog']

        self.token_id = access['token']['id']
        self.tenant_id = access['token']['tenant']['id']
        self.headers['token'] = {"X-Auth-Token": str(self.token_id)}

        for info_list in services:
            for info in info_list['endpoints']:
                if 'region' in info:
                    if not info['region'] in self.services:
                        self.services[info['region']] = [{info_list['name'] : info['publicURL']}]
                    else:
                        self.services[info['region']].append({info_list['name'] : info['publicURL']})

    def getAuthentication(self, user_name, api_key):
        """
        Get Authenticated with Rackspace so you can use the API.
        """
        auth_url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
        data = {"auth":
            {"RAX-KSKEY:apiKeyCredentials":
                {"username":user_name, "apiKey":api_key}}}
        headers = {'Content-type': 'application/json'}
        request_auth = requests.post(auth_url,
                                     data=json.dumps(data),
                                     headers=headers)
        authenticated_data = request_auth.json()

        self.buildDictFromAuth(authenticated_data)
        #self.prettyPrint(self.getDetailsByEndpoint('cloudServersOpenStack', ['token'], 'getSizes', 'dfw'))

    def getExtensions(self, path_key):
        for key in self.get_extensions:
            if key in path_key:
                return self.get_extensions[key]

    def getEndpointUrl(self, endpoint):
        """
        {'category':{ url:foo.bar, headers: {x-auth-token: token_id }, data: { } } }
        """
        urls = []
        for region in self.services:
            for url in self.services[region]:
                if endpoint in url:
                    urls.append(url[endpoint])
        return urls

    def getHeadersByType(self, list_of_headers):
        headers = {}
        for header_type in self.headers:
            for header_needed in list_of_headers:
                if header_needed in header_type:
                    for real_header in self.headers[header_needed]:
                        headers[real_header] = self.headers[header_needed][real_header]

        return headers

    def getFirstGenServers(self, account, header_list):
        url = 'https://servers.api.rackspacecloud.com/v1.0/' +\
                account +\
                self.getExtensions('getInstalledServers')
        headers = self.getHeadersByType(header_list)
        request_info = requests.get(url, headers=headers)
        json_data = request_info.json()
        raw_dump = json.dumps(json_data)
        formatted_json = json.loads(raw_dump)
        return formatted_json

    def getDetailsByEndpoint(self, endpoint, header_list, get_ext, region, container=""):
        for url_to_use in self.getEndpointUrl(endpoint):
            if region in url_to_use:
                if container:
                    url = url_to_use + container + self.getExtensions(get_ext)
                else:
                    url = url_to_use + self.getExtensions(get_ext)
        headers = self.getHeadersByType(header_list)
        request_info = requests.get(url, headers=headers)
        json_data = request_info.json()
        raw_dump = json.dumps(json_data)
        formatted_json = json.loads(raw_dump)
        return formatted_json

    def getCloudFilesContainers(self):
        tenant_id = 'MossoCloudFS_b151b4a5-26c0-41ed-8e48-abec10814e8f'
        containers_url = "https://storage101.dfw1.clouddrive.com/v1/" + tenant_id + '/test/' + "?format=json"
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

if __name__ == '__main__':
    rs_api = RsAPI()
    rs_api.run()
