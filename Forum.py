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

from Post import Post

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
    'allowed_content_types': ('Post',),
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
        'action': 'folder_localrole_form',
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
    Forum CPS
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
        """Return list of root posts (no replies)"""

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
        """Add a new post. Returns its id."""
        discussion = self.portal_discussion.getDiscussionFor(self)
        post_id = discussion.createReply(subject, message, author)
        post = discussion.getReply(post_id)
        post.in_reply_to = parent_id
        self.publishPost(post_id, not self.moderation_mode)
        return post_id

    def delPost(self, id):
        """Delete a post"""
        self.portal_discussion.getDiscussionFor(self).deleteReply(id)

    def publishPost(self, id, state=1):
        """Publish post <id>"""
        
        post = self.portal_discussion.getDiscussionFor(self).getReply(id)
        post.inforum = state
            
    def __getitem__(self, id):
        """Return post with id=<id>"""
        try:
            disc = self.portal_discussion.getDiscussionFor(self)
            reply = disc.getReply(id)
            result = self.getPostInfo(reply)
        except AttributeError:
            result = None

        return result

    def getPostReplies(self, post_id):
        """Return replies to post <post_id>"""
        discussion = self.portal_discussion.getDiscussionFor(self)
        # FIXME: is it really the right algorithm ?
        result = [ self.getPostInfo(post)
                   for post in discussion.objectValues()
                   if post.in_reply_to == post_id ]
        return result

    def getThreadInfo(self, post_id):
        """ getThreadInfo """
        post = self[post_id]
        while post['parent_id']:
            post = self[post['parent_id']]
            # raise "DEBUG", "parent is "+post

        return post

    def getDescendants(self, post_id):
        """
        Fetches post tree
        """
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
        """Sets up forum properties
        """
        #self.title = kw.get('title', self.title)
        #self.description = kw.get('description', self.description)

        CPSBaseDocument.edit(self,**kw)
        self.moderation_mode = kw.get('moderation_mode', 1)
        self.moderators = kw.get('moderators', [])

    security.declarePublic('getModerators')
    def getModerators(self, proxy):
        """XXX: docstring???"""
        all = mergedLocalRoles(proxy)
        result = []
        for user in all.keys():
            if 'ForumModerator' in all[user]:
                result.append(user)
        return result

    security.declarePublic('getOfficialModerators')
    def getOfficialModerators(self, proxy):
        """XXX: what is an "official moderator" ???"""
        moderator_list = self.getModerators(proxy)
        dtool = getToolByName(self, 'portal_metadirectories').members
        portal_url = getToolByName(self, 'portal_url').getPortalPath()
        dtool_entry_url = "%s/directory_getentry?dirname=%s&entry_id=" \
                          % (portal_url, dtool.id)
        result = []
        for moderator in moderator_list:
            mdata = {'id': moderator}
            mdata['fullname'] = \
                dtool.getEntry(moderator)[dtool.display_prop] or moderator
            mdata['homedir'] = dtool_entry_url + moderator
            result.append(mdata)
        return result

#def addCPSForumPost(self, id, **kw):
#    """function addCPSForumPost
#    """
#    post = CPSPost(id, **kw)
#    post.parent_id = kw['parent_id']
#    if post.parent_id is None:
#        post.parent_id = '_FORUM_'
#    self._setObject(id, post)
#
#
#class CPSPost(CPSBaseDocument, Post):
#    """Class Post for CPS
#    """
#    # Attributes:
#    meta_type = "CPSPost"
#    forum_meta_type = 'CPSForum'
#    _properties = CPSBaseDocument._properties + (
#        { 'id': 'text', 'type': 'string', 'mode': 'w',
#          'label': 'Post author' },
#        { 'id': 'author', 'type': 'string', 'mode': 'w',
#          'label': 'Post author' },
#        { 'id': 'forum_id', 'type': 'string', 'mode': 'w',
#          'label': 'Parent Forum id' },
#        { 'id': 'parent_id', 'type': 'string', 'mode': 'w',
#          'label': 'Parent Post id' },
#    )
#
#    def getPostInfo(self):
#        """Return post information as tuple (url, subject, author)"""
#        return (self.getId(), self.getSubject(), self.getAuthor())
#
#    #def __init__(self, id, **kw):
#    #    """Constructor"""
#    #    CPSBaseDocument.__init__(self, id, **kw)
