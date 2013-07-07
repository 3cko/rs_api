#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

import argparse
from rsapi import RsAPI


def ParseArgs():
    parser = argparse.ArgumentParser(
                            description="Rackspace API tool",
                            prog="CLI API Tool"
                                    )
    parser.add_argument('--username', '-u',
                        help="Account's username",
                        required=True,
                       )
    parser.add_argument('--api-key', '-k',
                        help="Account's API key",
                        required=True,
                       )
    parser.add_argument('--name', '-n',
                        help="Server or Cluser name",
                       )
    parser.add_argument('--web-nodes', '-wn',
                        help="Number of web nodes, OS and Size",
                        nargs=3,
                        metavar=('nodes', 'OS', 'size'),
                       )
    parser.add_argument('--database-nodes', '-mn',
                        help="Number of database nodes, OS and Size",
                        nargs=3,
                        metavar=('nodes', 'OS', 'size'),
                       )
    parser.add_argument('--next-gen', '-ng',
                        help="List Next Gen servers",
                        action="store_true",
                       )
    parser.add_argument('--first-gen', '-fg',
                        help="List First Gen servers",
                        action="store_true",
                       )
    parser.add_argument('--region', '-r',
                        help="List details by region",
                        required=True,
                       )
    parser.add_argument('--files', '-f',
                        help="List CloudFiles Containers",
                        action="store_true",
                       )
    parser.add_argument('--container', '-c',
                        help="List the files in the Cloud Files container",
                       )
    parser.add_argument('--list', '-l',
                        nargs=1,
                        choices=['os', 'sizes'],
                        help="List the available OS or Server Sizes",
                       )
    return parser.parse_args()

api = RsAPI()

args = ParseArgs()

api.getAuthentication(args.username, args.api_key)

if args.files:
    if not args.container:
        print "Cloud Files in " + args.region.upper()
        print '-' * 40
        api.parseCloudFiles(api.getDetailsByEndpoint("cloudFiles", ['token'], 'GetCloudFilesContainers', args.region))
    else:
        print "Cloud Files in " + args.container
        print '-' * 40
        container = '/' + args.container + '/'
        api.parseCloudFilesInContainer(api.getDetailsByEndpoint("cloudFiles", ['token'], 'GetCloudFilesContainers', args.region, container))
if args.next_gen:
    print "Cloud Servers in " + args.region.upper()
    print '-' * 40
    api.parseCurrentServers(api.getDetailsByEndpoint("cloudServersOpenStack", ['token'], 'getInstalledServers', args.region))
if args.first_gen:
    api.prettyPrint(api.getFirstGenServers(api.tenant_id, ['token']))
if args.list:
    if 'os' in args.list:
        api.parseOSList(api.getDetailsByEndpoint("cloudServersOpenStack", ['token'], 'getOS', args.region))
    elif 'sizes' in args.list:
        api.parseSizeList(api.getDetailsByEndpoint("cloudServersOpenStack", ['token'], 'getSizes', args.region))
if args.web_nodes:
    if args.name:
        node_count = 0
        nodes = args.web_nodes[0]
        os = args.web_nodes[1]
        size = args.web_nodes[2]
        for node in range(int(nodes)):
            server_name = 'WEB ' + "{0:02d} ".format(node + 1) + args.name
            print api.createServer(server_name, os, size)
if args.database_nodes:
    if args.name:
        node_count = 0
        nodes = args.database_nodes[0]
        os = args.database_nodes[1]
        size = args.database_nodes[2]
        for node in range(int(nodes)):
            server_name = 'DB ' + "{0:02d} ".format(node + 1) + args.name
            print api.createServer(server_name, os, size)
