#
# (C) Copyright 2002 Nuxeo SARL <http://www.nuxeo.com/>
# This product is governed by a license. See LICENSE.txt file.
#

# Python
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

contentClasses = ()
contentConstructors = ()
fti = ()

tools = None

try:
    import Forum
    import CPS3DiscussionTool

    fti += Forum.factory_type_information
    contentClasses += (
            Forum.CPS3Forum,
            Forum.CPS3Post,
        )
    contentConstructors += (
            Forum.addCPS3Forum,
            Forum.addCPS3Post,
        )
    tools = (CPS3DiscussionTool.CPS3DiscussionTool,)
    registerDirectory('skins/cps3', globals())
except ImportError: pass

def initialize(registrar):
    utils.ContentInit('CPS Forum Content',
        content_types=contentClasses,
        permission=AddPortalContent,
        extra_constructors=contentConstructors,
        fti=fti
    ).initialize(registrar)

    if tools:
        utils.ToolInit(
            'CPS Discussion Tool',
            tools = tools,
            product_name = 'CPS Forum',
            icon = 'tool.gif',
            ).initialize(registrar)

