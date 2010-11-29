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

from django.conf.urls.defaults import *
from ots.server.django_logger.views import *

urlpatterns = patterns('',
    (r'^view/workers/$', view_workers),
    (r'^view/workers/(?P<remote_host>\S+)/$', view_worker_details),
    (r'^view/filtter/$', filtter_message_viewer),
    (r'^(?P<servicename>\w+)/(?P<run_id>\w+)/$', create_message),
    (r'^view/$', main_page),
    (r'^view/testrun/(?P<run_id>\w+)/$', basic_testrun_viewer),
    (r'^view/details/(?P<log_id>\w+)/$', view_message_details),
)
