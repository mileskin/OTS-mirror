# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

"""
A simple forking xmlrpc server for serving the ots public interface
"""

import os
import sys
import configobj

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ForkingMixIn
from ots.server.server_config_filename import server_config_filename
from ots.server.hub.api import Hub 
from ots.server.distributor.api import TaskRunner

################################
# HACKISH TESTING CAPABILITIES
################################

DEBUG = False

if DEBUG:
    from ots.server.hub.tests.component.mock_taskrunner import \
                                       MockTaskRunnerResultsPass
    
###########################
# OTS FORKING SERVER
###########################

class OtsForkingServer(ForkingMixIn, SimpleXMLRPCServer):
    pass

def _config():
    """
    rtype: C{Tuple) of C{str} and C{int}
    rparam: hostname, port
    """
    config_file = server_config_filename()
    config = configobj.ConfigObj(config_file).get("ots.server.xmlrpc")
    return config.get('host'), config.as_int('port')


#############################
# REQUEST_SYNC
#############################

def request_sync(sw_product, request_id, notify_list, options_dict):
    """
    Convenience function for the interface for the hub.
    Processes the raw parameters and fires a testrun

    @type sw_product: C{str}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{str}
    @param request_id: An identifier for the request from the client

    @type notify_list: C{list}
    @param notify_list: Email addresses for notifications

    #FIXME legacy interface 
    @type options_dict: C{dict}
    @param options_dict: A dictionary of options
    """
    
    try:
        options_dict["notify_list"] = notify_list
        hub = Hub(sw_product, request_id, **options_dict)
        if DEBUG:
            hub._taskrunner = MockTaskRunnerResultsPass()
        if hub.run():
            return "PASS"
        else:
            return "FAIL"
    except:
        return "ERROR"

    
def main(is_logging = False):
    """
    Top level script for XMLRPC interface
    """
    server = OtsForkingServer(_config(), SimpleXMLRPCRequestHandler)
    server.register_function(request_sync)
    print "Starting OTS xmlrpc server..."
    print 
    print "Host: %s, Port: %s" % _config()
    print 

    if is_logging:
        import logging
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(log_handler)
    
    server.serve_forever()

if __name__ == "__main__":
    is_logging = False
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        is_logging = True
    main(is_logging)
