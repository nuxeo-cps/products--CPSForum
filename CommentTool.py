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
from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import getSecurityManager,\
     newSecurityManager

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import ManagePortal, View,\
     ModifyPortalContent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CPSCore.EventServiceTool import getEventService

from Forum import addCPSForum

from CPSForumPermissions import ForumManageComments


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

    _data = {}

    def __init__(self):
        PortalFolder.__init__(self, self.id)

    #
    # ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainCommentTool', globals())

    security.declarePublic('getCommentForumURL')
    def getCommentForumURL(self, object_url):
        return self._data.get(object_url, '')

    security.declarePublic('getCommentedDocument')
    def getCommentedDocument(self, forum_url):
        for doc_url, frm_url in self._data.items():
            if frm_url == forum_url:
                return doc_url
        return None

    security.declareProtected(View, 'registerCommentForum')
    def registerCommentForum(self, proxy_path='', forum_path=''):
        data = self._data
        data[proxy_path] = forum_path
        self._data = data

    security.declarePublic('isCommentingAllowedFor')
    def isCommentingAllowedFor(self, proxy):
        """Return a boolean indicating whether comments are allowed for the
        specified proxy/content"""
        # depending on the client's
        # product, metadata's allow_discussion might not be read-only
        # so check that there is actuall a forum for this document
        proxy_url = proxy.absolute_url(relative=1)
        if proxy_url in self._data.keys():
            return 1
        else:
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

    security.declareProtected(View, 'notify_document_deleted')
    def notify_document_deleted(self, event_type, object, infos):
        doc_url = object.absolute_url(relative=1)
        data = self._data
        if self._data.has_key(doc_url):
            del data[doc_url]
            self._data = data

    security.declareProtected(View, 'getForum4Comments')
    def getForum4Comments(self, proxy_doc):
        """Get current document's commenting forum ; create it if it does not exist

        Lazy instantiation"""

        forum = None
        portal = getToolByName(self, 'portal_url').getPortalObject()

        # check whether the forum object exists or not
        forum_url = self.getCommentForumURL(proxy_doc.absolute_url(relative=1))
        if forum_url:
            forum = self.restrictedTraverse(forum_url)

        # if not create it
        if not forum:
            no_content_wf_chain = {}
            #XXX: would be cleaner if based on .cps_worfklow_configuration's
            #     declared chains
            for ptype in portal.portal_types.objectIds():
                no_content_wf_chain[ptype] = ''
            #create a wf and add chains to it
            def wfSetup(folder, chains):
                if not '.cps_workflow_configuration' in folder.objectIds():
                    folder.manage_addProduct['CPSWorkflow'].addConfiguration()
                    wfc = getattr(folder, '.cps_workflow_configuration')
                    for type, chain in chains.items():
                        wfc.manage_addChain(portal_type=type, chain=chain)

            # check whether the forum object exists or not
            # if not create it (also create .discussions if necessary)
            def getParentFolder(proxy):
                """Returns 'Section' or 'Workspace' parent folder."""
                parent = proxy.aq_inner.aq_parent
                while parent:
                    if hasattr(parent, 'portal_type') and \
                           (parent.portal_type == 'Section' or
                            parent.portal_type == 'Workspace'):
                        return parent
                    parent = parent.aq_inner.aq_parent
                return proxy.aq_inner.aq_parent

            parent_folder = getParentFolder(proxy_doc)

            class CPSUnrestrictedUser(UnrestrictedUser):
                """Unrestricted user that still has an id.

                Taken from CPSMembershipTool
                """

                def getId(self):
                    """Return the ID of the user."""
                    return self.getUserName()


            mtool = getToolByName(self, 'portal_membership')
            old_user = getSecurityManager().getUser()

            tmp_user = CPSUnrestrictedUser('root', '',
                                           ['Manager', 'Member'], '')
            tmp_user = tmp_user.__of__(mtool.acl_users)
            newSecurityManager(None, tmp_user)

            # we should create a Workspace if parent folder is a workspace
            # or a Section if parent folder is a section
            folder_type = parent_folder.portal_type

            if '.cps_discussions' not in parent_folder.objectIds():
                portal.portal_workflow.invokeFactoryFor(parent_folder, folder_type, '.cps_discussions')
            cpsmcat = portal.Localizer.default
            discussion_folder = getattr(parent_folder, '.cps_discussions')
            kw = {'hidden_folder': 1,
                  'Title': cpsmcat('forum_title_comments').encode('ISO-8859-15', 'ignore')}
            discussion_folder_c = discussion_folder.getEditableContent()
            discussion_folder_c.edit(**kw)
            comment_wf_chain = no_content_wf_chain.copy()
            if folder_type == 'Section':
                forum_wf_chain = 'section_forum_wf'
            else:
                forum_wf_chain = 'workspace_forum_wf'
            comment_wf_chain.update({'CPSForum': forum_wf_chain,
                                     'ForumPost': 'forum_post_wf',
                                     })
            wfSetup(discussion_folder, comment_wf_chain)
            portal.portal_eventservice.notifyEvent('modify_object', discussion_folder, {})
            portal.portal_eventservice.notifyEvent('modify_object', discussion_folder_c, {})
            existing_forum_ids = discussion_folder.objectIds()
            # forum's id is computed using the std script
            forum_id = portal.computeId(compute_from=proxy_doc.id,
                                        location=discussion_folder.this())
            portal.portal_workflow.invokeFactoryFor(discussion_folder,
                                                    'CPSForum', forum_id)
            forum = getattr(discussion_folder, forum_id)
            forum_c = forum.getEditableContent()
            kw = {'Title': cpsmcat('forum_title_comments_for').encode('ISO-8859-15', 'ignore')+' '+proxy_doc.Title(),
                  'Description': cpsmcat('forum_desc_comments').encode('ISO-8859-15', 'ignore')+' '+proxy_doc.Title(),
                  'moderation_mode': 0}
            forum_c.edit(**kw)
            portal.portal_eventservice.notifyEvent('modify_object', forum, {})

            # tell comment_tool that it is now activated and map it
            portal.portal_discussion.registerCommentForum(proxy_path=proxy_doc.absolute_url(relative=1),
                                                          forum_path=forum.absolute_url(relative=1))

            newSecurityManager(None, old_user)

        return forum

    #XXX: portal_discussion might not be the best place for such a method
    # as it is used for all forums, not just comment forums. But I don't
    # want to create yet another tool just for that, and there is no better
    # place for now (Forum.py is not an option as an anon user cannot do
    # proxy_forum.getContent() from the forum_post script).
    def createAnonymousForumPost(self, proxy_forum, post_id, subject,
                                 author, message, parent_id):
        """Post a message as an anonymous user

        Because anonymous posts require more rights than an anon user has"""

        wtool = getToolByName(self, 'portal_workflow')
        # temp switch to unrestricted user
        class CPSUnrestrictedUser(UnrestrictedUser):
            """Unrestricted user that still has an id.

            Taken from CPSMembershipTool
            """

            def getId(self):
                """Return the ID of the user."""
                return self.getUserName()
        mtool = getToolByName(self, 'portal_membership')
        old_user = getSecurityManager().getUser()
        tmp_user = CPSUnrestrictedUser('anonymous__forum__poster', '',
                                       ['Manager', 'Member'], '')
        tmp_user = tmp_user.__of__(mtool.acl_users)
        newSecurityManager(None, tmp_user)
        # create post
        wtool.invokeFactoryFor(proxy_forum, 'ForumPost', post_id,
                               subject=subject, author=author,
                               message=message, parent_id=parent_id)
        forum = proxy_forum.getContent()
        forum.newPostCreated(post_id, proxy=proxy_forum)
        # leave unrestricted user mode
        newSecurityManager(None, old_user)

    security.declareProtected(ForumManageComments, 'setAllowDiscussion')
    def setAllowDiscussion(self, proxy, allow):
        """Set discussion allowed or not"""

        class CPSUnrestrictedUser(UnrestrictedUser):
            """Unrestricted user that still has an id.

            Taken from CPSMembershipTool
            """

            def getId(self):
                """Return the ID of the user."""
                return self.getUserName()


        mtool = getToolByName(self, 'portal_membership')
        old_user = getSecurityManager().getUser()

        tmp_user = CPSUnrestrictedUser('root', '',
                                       ['Manager', 'Member'], '')
        tmp_user = tmp_user.__of__(mtool.acl_users)
        newSecurityManager(None, tmp_user)

        kw = {'allow_discussion': allow,}
        proxy.getEditableContent().edit(**kw)

        newSecurityManager(None, old_user)


InitializeClass(CommentTool)
