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
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CPSCore.EventServiceTool import getEventService

from Forum import addCPSForum


class CommentTool(UniqueObject, PortalFolder, DiscussionTool):
    """Comment tool, a container for forums used to comment documents."""

    id = 'portal_discussion'
    meta_type = 'CPS Discussion Tool'

    security = ClassSecurityInfo()
    
    manage_options = (ActionProviderBase.manage_options +
                      PortalFolder.manage_options[:1] + 
                      ({'label': 'Overview', 'action': 'manage_overview'},) +
                      PortalFolder.manage_options[1:])

    _actions = ()

    def __init__(self):
        PortalFolder.__init__(self, self.id)

    #
    # ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainCommentTool', globals())

    #
    # 'portal_comment' interface methods
    # FIXME: there is no such 'portal_comment' interface. Is it supposed
    # to be portal_discussion (it is not: method names are not exactly the
    # same) ???
    #
    security.declarePublic('getDiscussionForumFor')
    def getDiscussionForumFor(self, proxy):
        """Get the CPSForum object that applies to this proxy/doc"""
        doc_id = proxy.getDocid()
        if doc_id in self.objectIds():
            return self.getForum(doc_id)
        else:
            return None

    security.declarePublic('isCommentingAllowedFor')
    def isCommentingAllowedFor(self, proxy):
        """Return a boolean indicating whether comments are allowed for the
        specified proxy/content"""
        content = proxy.getContent()
        if hasattr(content, 'allow_discussion'):
            return content.allow_discussion
        typeInfo = getToolByName(self, 'portal_types').getTypeInfo(content)
        if typeInfo:
            return typeInfo.allowDiscussion()
        return 0

    #
    # Other methods
    #
    security.declarePublic('getForum')
    def getForum(self, forum_id):
        return getattr(self, forum_id, None)

    security.declarePublic('addForum')
    def addForum(self, doc):
        doc_id = doc.getDocid()
        if not doc_id in self.objectIds():
            # This is the first comment about this doc:
            # create a new forum, with id matching the one of the document
            # (this adds the forum directly to portal_comment)
            addCPSForum(self, doc_id)
        return self.getForum(doc_id)

    security.declarePublic('notifyPostCreation')
    def notifyPostCreation(self, object, url_to_display=None, comment=0):
        """Notify the event service tool that an new post or comment
        has been created

        We need to call it from the skins to make the difference in between
        post and comment and as well to give the event_service the URL of
        the post to display
        (i.e: http://cps.bar.com/forum/forum_view_thread?post_id=4444)
        Notice, the URL is coompletly different form the URL of the
        post object itself
        """
        evtool = getEventService(self)

        #
        # We want to separate these two types of events
        # Normal post / Commment
        #
        if comment:
            event_id = 'forum_comment_create'
        else:
            event_id = 'forum_new_message'

        evtool.notify(event_id, object, {'url_to_display': url_to_display})

InitializeClass(CommentTool)
