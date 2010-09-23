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
Runs an OTS Testrun 
"""

import logging

from ots.common.dto.api import Packages, Results, Environment

from ots.server.distributor.api import TASKRUNNER_SIGNAL

from ots.results.api import parse_results
from ots.results.api import TestrunResult
from ots.results.api import is_valid_run

LOG = logging.getLogger(__name__)

class Testrun(object):
    """
    Holds the metadata associated with a Testrun 
    
    Wraps the handlers and runner and hooks up the results

    Closely associated with the Taskrunner
    """
    
    def __init__(self, 
                 run_test,
                 is_hw_enabled = True,
                 is_host_enabled = False,
                 insignificant_tests_matter = True):
        """
        @type run_test: C{callable} The callable to run
        @param run_test: The callable to run
        @type is_hw_enabled: C{bool} 
        @param is_hw_enabled: Flag

        @type is_host_enabled: C{bool}
        @param is_host_enabled: Flag

        @type insignificant_tests_matter: C{bool} 
        @param insignificant_tests_matter: Flag
        """
        #FIXME: Callable added for testability 
        #One advantage of having the distributor 
        #as a separate component is that it
        #might help improve this API
        self._run_test = run_test
        self.is_hw_enabled = is_hw_enabled
        self.is_host_enabled = is_host_enabled
        self.insignificant_tests_matter = insignificant_tests_matter
        #
        self.results_xmls = []
        self.tested_packages = None
        self.expected_packages = None

    ###########################################
    # HANDLERS
    ###########################################

    def _taskrunner_cb(self, signal, dto, **kwargs):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type dto: L{ots.common.dto}
        @param dto: An OTS datatype

        The callback for TASKRUNNER_SIGNAL delegates
        data to handler depending on MESSAGE_TYPE
        """
        if isinstance(dto, Exception):
            raise dto
        elif isinstance(dto, Results):
            self._results(dto)
        elif isinstance(dto, Packages):
            self._packages(dto)
        else:
            LOG.debug("Unknown Message Type: '%s'"%(message))

    def _results(self, result):
        """
        @type result: L{ots.common.api.ResultObject}
        @param result: The Results Objects

        Handler for Results
        """
        environment = result.environment
        LOG.debug("Received results for %s"%(environment))
        packages = Packages(environment, [result.package])
        print packages
        if self.tested_packages is None:
            self.tested_packages = packages
        else:
            self.tested_packages.update(packages)
        self.results_xmls.append(result.results_xml)

    def _packages(self, packages): 
        """
        @type packages: L{ots.common.dto.environment.packages}
        @param packages: The Packages

        Handler for Packages
        """
        LOG.debug("Received packages: %s" % (packages))
        if self.expected_packages is None:
            self.expected_packages = packages
        else:
            self.expected_packages.update(packages)

    #############################################
    # HELPERS
    #############################################
            
    def _go_nogo(self):
        """
        @rtype: L{TestrunResult}
        @return: PASS / FAIL / NO_CASES
        """
        #FIXME this should be moved out into own module
        ret_val = TestrunResult.NO_CASES
        aggregated_results = []
        for results_xml in self.results_xmls:
            all_passed = parse_results(results_xml.read(),
                                       self.insignificant_tests_matter)
            if all_passed is not None:
                aggregated_results.append(all_passed)
        if aggregated_results:
            if all(aggregated_results):
                ret_val = TestrunResult.PASS
            else:
                ret_val = TestrunResult.FAIL
        return ret_val

    ####################################################
    # PUBLIC METHOD
    ####################################################

    def run(self):
        """
        @rtype: L{TestrunResult}
        @return: PASS / FAIL / NO_CASES
        
        Run...
        """
        ret_val = TestrunResult.FAIL
        TASKRUNNER_SIGNAL.connect(self._taskrunner_cb)
       
        self._run_test()
        is_valid_run(self.expected_packages,
                     self.tested_packages,
                     self.is_hw_enabled,
                     self.is_host_enabled)
        ret_val = self._go_nogo()
        return ret_val
