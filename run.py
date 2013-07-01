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
    """
    parser.add_argument('--name', '-n',
                        help="Server or Cluser name",
                       )
    parser.add_argument('--web-nodes', '-wn',
                        help="Number of webnodes, OS and Size",
                        nargs=3,
                       )
    parser.add_argument('--mysql-nodes', '-mn',
                        help="Number of webnodes, OS and Size",
                        nargs=3,
                       )
    """
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
        api.prettyPrint(api.getDetailsByEndpoint("cloudServersOpenStack", ['token'], 'getInstalledServers', args.region))
if args.first_gen:
        api.prettyPrint(api.getFirstGenServers(api.tenant_id, ['token']))
