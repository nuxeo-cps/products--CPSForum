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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, \
     ManageProperties, ChangePermissions
from Products.CMFCore.utils import mergedLocalRoles
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder

from Products.CPSCore.EventServiceTool import getEventService

#from Post import Post

from zLOG import LOG, DEBUG

factory_type_information = ({
    'id': 'Forum',
    'meta_type': 'CPSForum',
    'description': "portal_type_CPSForum_description",
    'icon': 'forum_icon.gif',
    'title': "portal_type_CPSForum_title",
    'product': 'CPSForum',
    'factory': 'addCPSForum',
    'filter_content_types': 1,
    'allowed_content_types': (),
    'immediate_view': 'forum_edit_form',
    'allow_discussion': 0,
    'actions': ({
        'id': 'view',
        'name': 'action_view',
        'action': 'forum_view',
        'permissions': (View,),
    }, {
        'id': 'create',
        'name': 'action_create',
        'action': 'forum_create_form',
        'visible': 0,
        'permissions': ('',)
    }, {
        'id': 'edit',
        'name': 'action_modify',
        'action': 'forum_edit_form',
        'permissions': (ManageProperties,),
    }, {
        'id': 'localroles',
        'name': 'action_local_roles',
        'action': 'forum_localrole_form',
        'permissions': (ChangePermissions,),
    }, {
        'id': 'isfunctionalobject',
        'name': 'isfunctionalobject',
        'action': 'isfunctionalobject',
        'visible': 0,
        'permissions': ('',),
    }, {
        'id': 'isproxytype',
        'name': 'isproxytype',
        'action': 'document',
        'visible': 0,
        'permissions': ('',),
    }, {
        'id': 'issearchabledocument',
        'name': 'issearchabledocument',
        'action': 'issearchabledocument',
        'visible': 0,
        'permissions': ('',),
    },),
},)


def addCPSForum(self, id, **kw):
    """
    Add a Forum
    """
    forum = CPSForum(id, **kw)
    self.moderation_mode = kw.get('moderation_mode', 1)
    CPSBase_adder(self, forum)


class CPSForum(CPSBaseDocument):
    """
    CPS Forum definition
    """
    meta_type = 'CPSForum'
    portal_type = 'CPSForum'
    # XXX: is it needed ?
    allow_discussion = 1
    moderation_mode = 1 # after publishing post
    moderators = []
    security = ClassSecurityInfo()

    #def __init__(self, id, **kw):
    #    """Constructor"""
    #    CPSBaseDocument.__init__(self,id, **kw)

    def getThreads(self):
        """Return a list of root posts

        Does not return replies to post, just thread root posts
        """

        discussion = self.portal_discussion.getDiscussionFor(self)
        result = [ self.getPostInfo(post)
                   for post in discussion.getReplies()
                   if post.in_reply_to is None ]
        return result

    def getPostInfo(self, post):
        """Return post information as a dictionnary"""
        # NB: It looks like we're obliged to maintain
        # our own 'publication state' for the post,
        # but it should be hidden behind a WF
        # on the portal type
        #
        # ... provided the Post has been
        # chosen to effectively be a Portal type,
        # which dosen't apply here
        #
        # XXX: strange, 'self' is not used in this method. Does it
        # really belong to this class ?
        return {
            'id': post.id, 'subject': post.title, 'author': post.creator,
            'message': post.text, 'parent_id': post.in_reply_to,
            'published': hasattr(post, 'inforum') and post.inforum,
            'modified': post.bobobase_modification_time(),
        }

    def addPost(self, subject="", message="", author="", parent_id=None):
        """Add a new post

        Returns the new post's id."""
        discussion = self.portal_discussion.getDiscussionFor(self)
        post_id = discussion.createReply(subject, message, author)
        post = discussion.getReply(post_id)
        post.in_reply_to = parent_id
        self.publishPost(post_id, not self.moderation_mode)
        return post_id

    def delPost(self, id):
        """Delete a post

        The post is refered to by its id"""
        self.portal_discussion.getDiscussionFor(self).deleteReply(id)

    def publishPost(self, id, state=1):
        # XXX: this method name must be changed, since is it also used
        # to change post state.
        """Publish post <id>"""
        post = self.portal_discussion.getDiscussionFor(self).getReply(id)
        # XXX: this breaks encapsulation. Fix this.
        post.inforum = state

    def notifyPostCreation(self, url_to_display=None, comment=0):
        """ Notify the event service tool that an new post or comment
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
        # We want to separate thes two types of events
        # Normal post / Commment
        #

        if comment:
            event_id = 'forum_comment_create'
        else:
            event_id = 'forum_new_message'

        evtool.notify(event_id,
                      self,
                      {'url_to_display':url_to_display})

    def __getitem__(self, id):
        """Return postinfo

        Returns information (structured as a dictionnary) about post
        with id=<id>, or None if there is no such post."""
        # XXX: shouldn't it raise KeyError in the latter case ?
        try:
            disc = self.portal_discussion.getDiscussionFor(self)
            reply = disc.getReply(id)
            result = self.getPostInfo(reply)
        except AttributeError:
            result = None
        return result

    def getPostReplies(self, post_id):
        """Return replies to root post

        Root post is refered to by <post_id>"""
        discussion = self.portal_discussion.getDiscussionFor(self)
        # FIXME: is it really the right algorithm ?
        result = [ self.getPostInfo(post)
                   for post in discussion.objectValues()
                   if post.in_reply_to == post_id ]
        return result

    def getDescendants(self, post_id):
        """Fetch post tree"""
        info_getter = self.getPostInfo
        discussion = self.portal_discussion.getDiscussionFor(self)
        father = discussion.getReply(post_id)
        result = ()

        # ul
        for i in discussion.objectValues():
            if i.in_reply_to == father.id:
                branch = (info_getter(i),) # one item
                branch += (self.getDescendants(i.id),) # one list
                result += (branch,)

        return result

    def editForumProperties(self, **kw):
        """Edit forum properties
        """
        #self.title = kw.get('title', self.title)
        #self.description = kw.get('description', self.description)

        CPSBaseDocument.edit(self,**kw)
        self.moderation_mode = kw.get('moderation_mode', 1)
        self.moderators = kw.get('moderators', [])

    security.declarePublic('getModerators')
    def getModerators(self, proxy):
        """Get moderators of this forum"""
        all = mergedLocalRoles(proxy)
        result = []
        for user_id in all.keys():
            if 'ForumModerator' in all[user_id]:
                result.append(user_id)
        return result

    security.declarePublic('getOfficialModerators')
    def getOfficialModerators(self, proxy):
        """XXX: what is an 'official moderator' ???"""
        moderator_list = self.getModerators(proxy)
        dtool = getToolByName(self, 'portal_metadirectories').members
        portal_url = getToolByName(self, 'portal_url').getPortalPath()
        # XXX: this is dangerous. This URL may change one day. We need
        # an API.
        dtool_entry_url = "%s/directory_getentry?dirname=%s&entry_id=" \
                          % (portal_url, dtool.id)
        result = []
        for moderator_id in moderator_list:
            mdata = {'id': moderator_id}
            entry = dtool.getEntry(moderator_id)
            if entry:
                mdata['fullname'] = entry[dtool.display_prop] or moderator_id
            else:
                mdata['fullname'] = moderator_id
            mdata['homedir'] = dtool_entry_url + moderator_id
            result.append(mdata)
        return result
