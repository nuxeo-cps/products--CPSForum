# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga <ep@nuxeo.com>
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
"""The Comment tool manages comments associated with documents and
displayed using the CPSForum interface
"""

from zLOG import LOG, DEBUG
from utilities import _dtmldir
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName

from Forum import addCPSForum

class CommentTool(UniqueObject, PortalFolder):
    """Comment tool, a container for forums used to comment documents."""

    id = 'portal_comment'
    meta_type = 'Comment Tool'

    security = ClassSecurityInfo()
    
    manage_options = (PortalFolder.manage_options[:1] + 
                      ({'label': 'Overview', 'action': 'manage_overview'},) +
                      PortalFolder.manage_options[1:])

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('explainCommentTool', _dtmldir)
    
    def __init__(self):
        PortalFolder.__init__(self, self.id)

    #
    #   'portal_comment' interface methods
    #
    security.declarePublic('getDiscussionFor')
    def getDiscussionFor(self, proxy):
        '''Get the CPSForum object that applies to this proxy/doc
        '''

        doc_id = proxy.getDocid()
        if doc_id in self.contentIds():
            return self.getForum(doc_id)
        else:
            return None

    security.declarePublic('isCommentingAllowedFor')
    def isCommentingAllowedFor(self, proxy):
        '''Return a boolean indicating whether comments are
           allowed for the specified proxy/content
        '''

        content = proxy.getContent()
        if hasattr(content, 'allow_discussion'):
            return content.allow_discussion
        typeInfo = getToolByName(self, 'portal_types').getTypeInfo(content)
        if typeInfo:
            return typeInfo.allowDiscussion()
        return 0

    security.declarePublic('getForum')
    def getForum(self, forum_id):
        for item in self.contentItems():
            if item[0] == forum_id:
                return item[1]
        return None

    security.declarePublic('addForum')
    def addForum(self, doc):
        doc_id = doc.getDocid()
        if not doc_id in self.contentIds():
            #this is the first comment about this doc
            #create a new forum, with id matching the one of the document
            #(this adds the forum directly to portal_comment)
            addCPSForum(self, doc_id)
        return self.getForum(doc_id)

InitializeClass(CommentTool)
