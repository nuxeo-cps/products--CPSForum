#
# (C) Copyright 2002 Nuxeo SARL <http://www.nuxeo.com/>
# This product is governed by a license. See LICENSE.txt file.
#

# Python
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import Forum
contentClasses = ()
contentConstructors = ()
fti = ()

fti += Forum.factory_type_information
contentClasses += (
    Forum.CPSForum,
    Forum.CPSPost,
    )
contentConstructors += (
    Forum.addCPSForum,
    Forum.addCPSPost,
    )
registerDirectory('skins/forum_default', globals())

def initialize(registrar):
    utils.ContentInit('CPS Forum Content',
        content_types=contentClasses,
        permission=AddPortalContent,
        extra_constructors=contentConstructors,
        fti=fti
    ).initialize(registrar)

