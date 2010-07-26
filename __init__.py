# (C) Copyright 2002, 2003 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

# Python
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent
from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CPSCore.interfaces import ICPSSite


import Forum
import CommentTool
import fields

contentClasses = ()
contentConstructors = ()
fti = ()

fti += Forum.factory_type_information
contentClasses += (Forum.CPSForum,)
contentConstructors += (Forum.addCPSForum,)

registerDirectory('skins/forum_default', globals())

tools = (CommentTool.CommentTool,)

def initialize(registrar):
    utils.ContentInit('CPS Forum Content',
        content_types=contentClasses,
        permission=AddPortalContent,
        extra_constructors=contentConstructors,
        fti=fti
    ).initialize(registrar)
    utils.ToolInit('CPS Discussion Tool',
        tools=tools,
        icon='tool.png',
    ).initialize(registrar)
    
    profile_registry.registerProfile(
        'default',
        'CPS Forum',
        "Forum product for CPS.",
        'profiles/default',
        'CPSForum',
        EXTENSION,
        for_=ICPSSite)
