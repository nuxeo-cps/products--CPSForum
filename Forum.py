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
from Acquisition import aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, ChangePermissions
from Products.CPSCore.CPSBase import CPSBase_adder
from Products.CPSCore.EventServiceTool import getEventService
try:
    from Products.CPSDocument.CPSDocument import CPSDocument as BaseDocument
except ImportError:
    from Products.CPSCore.CPSBase import CPSBaseDocument as BaseDocument
from CPSForumPermissions import ForumModerate
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from zLOG import LOG, DEBUG, INFO

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
    'allow_discussion': 1,
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
        'id': 'new_thread',
        'name': 'new_thread',
        'action': 'forum_post_form',
        'permissions': ('Modify Folder Properties',),
    }, {
        'id': 'edit',
        'name': 'action_modify',
        'action': 'forum_edit_form',
        'permissions': ('Modify Folder Properties',),
    }, {
        'id': 'localroles',
        'name': 'action_local_roles',
        'action': 'forum_localrole_form',
        'permissions': (ChangePermissions,),
    }, ),
    'cps_proxy_type': 'folder',
    'cps_is_searchable': 1,
},)


def addCPSForum(self, id, REQUEST=None, **kw):
    """Add a Forum."""
    ob = CPSForum(id, **kw)
    CPSBase_adder(self, ob, REQUEST=REQUEST)

class CPSForum(BaseDocument):
    """CPS Forum definition."""
    meta_type = 'CPSForum'
    portal_type = 'CPSForum'

    _properties = BaseDocument._properties + (
        {'id':'moderation_mode', 'type':'selection', 'mode':'w',
         'select_variable': 'all_moderation_mode', 'label':'Moderation mode'},
        {'id':'allow_anon_posts', 'type':'boolean', 'mode':'w',
         'label':'Allow anonymous posts'},
        {'id':'send_moderation_notification', 'type':'boolean', 'mode':'w',
         'label':'Send moderation notification'},
        {'id':'frozen_forum', 'type':'boolean', 'mode':'w',
         'label':'Frozen forum'},
        )

    allow_discussion = 1
    all_moderation_mode = (0, 1)  #0=a posteriori, 1=a priori
    moderation_mode = 1
    allow_anon_posts = 0
    send_moderation_notification = 0
    # if frozen, no longer possible to post messages
    frozen_forum = 0
    moderators = []
    security = ClassSecurityInfo()
    # contains root post ids of locked threads (these are the IDs
    # of post documents, not post proxies)
    locked_threads = []

    security.declareProtected(View, 'newPostCreated')
    def newPostCreated(self, post_id, proxy=None):
       """Do some processing related to the creation of a new post

       Does not actually create the post (handled in calling script)
       """
       evtool = getEventService(self)

       notified = 0

       # Is a post creation within a forum thread ?
       current_post =  getattr(proxy, post_id)
       info = self.getPostInfo(current_post)
       if info['parent_id']:
           event_id = 'forum_new_post'
           notified = 1
           evtool.notify(event_id, current_post, infos={})

       if not notified:
           # Lookup within the Forum
           event_id = ''
           if aq_parent(aq_inner(proxy)).id == '.cps_discussions':
               event_id = 'forum_new_comment'
           else:
               event_id = 'forum_new_post'

           if event_id:
               evtool.notify(event_id, proxy, infos={})

    security.declareProtected(View, 'newPostPublished')
    def newPostPublished(self, post_id, proxy=None):
       """Do some processing related to the publication of a new post

       Does not actually publish the post (handled in calling script)
       """
       evtool = getEventService(self)
       event_id = ''
       if aq_parent(aq_inner(proxy)).id == '.cps_discussions':
           event_id = 'forum_comment_published'
       else:
           event_id = 'forum_post_published'
       if event_id:
           evtool.notify(event_id, proxy, infos={})

    security.declareProtected(ForumModerate, 'delPosts')
    def delPosts(self, posts, proxy=None):
        """Delete a list of posts from this forum

        Sync data structures such as the locked thread list"""

        for post in posts:
            pid = getattr(proxy, post).getContent().id
            if pid in self.locked_threads:
                self.locked_threads.remove(pid)
        proxy.manage_delObjects(posts)

    security.declareProtected(View, 'getThreads')
    def getThreads(self, proxy=None):
        """Return a list of root posts

        Does not return replies to post, just thread root posts
        """

        if proxy:
            #retrieve all root posts
            result = [self.getPostInfo(post)
                      for post in proxy.objectValues(['CPS Proxy Document']) #[x for x in proxy.objectValues() if x.meta_type == 'CPS Proxy Document']
                      if  post.getContent().parent_id is None]
        else:
            discussion = self.portal_discussion.getDiscussionFor(self)
            result = [ self.getPostInfo(post, discussion=1)
                       for post in discussion.getReplies()
                       if post.in_reply_to is None ]
        return result

    security.declareProtected(View, 'getPostInfo')
    def getPostInfo(self, post, discussion=0):
        """Return post information as a dictionnary"""
        # discussion is true if processing a post represented
        # as a Discussion Item instead of a ForumPost

        if discussion:
            post_doc = post.getContent()
            return {'id': post.id, 'subject': post.title, 'author': post_doc.author,
                    'message': post.text, 'parent_id': post.in_reply_to,
                    'published': hasattr(post, 'inforum') and post.inforum,
                    'modified': post.bobobase_modification_time(),
                    'locked': post.id in self.locked_threads
                    }
        else:
            post_doc = post.getContent()
            wtool = getToolByName(self, 'portal_workflow')
            r_state = wtool.getInfoFor(post, 'review_state', 'nostate')
            return {
                'id': post.id, 'subject': post.Title(), 'author': post_doc.author,
                'message': post_doc.Description(), 'parent_id': post_doc.parent_id,
                'published': r_state == 'published',
                'modified': post_doc.bobobase_modification_time(),
                'locked': post_doc.id in self.locked_threads
                }

    security.declareProtected(ForumModerate, 'changePostPublicationStatus')
    def changePostPublicationStatus(self, id, status=1):
        """(Un)Publish post <id>"""
        post = self.portal_discussion.getDiscussionFor(self).getReply(id)
        # XXX: this breaks encapsulation. Fix this.
        post.inforum = status

    security.declareProtected(View, 'getDescendants')
    def getDescendants(self, post_id, proxy=None):
        """Fetch post tree"""
        info_getter = self.getPostInfo
        if proxy:
            posts = proxy.objectValues(['CPS Proxy Document']) #[x for x in proxy.objectValues() if x.meta_type == 'CPS Proxy Document']

        result = ()

        for post in posts:
            if post.getContent().parent_id == post_id:
                branch = (self.getPostInfo(post),) # one item
                branch += (self.getDescendants(post.id, proxy=proxy),) # one list
                result += (branch,)

        return result

    security.declarePrivate('getRootPost')
    def getRootPost(self, post_id, proxy=None):
        """get the root post of thread to which post_id belongs to"""

        post_proxy = getattr(proxy, post_id)
        post_doc = post_proxy.getContent()
        while post_doc.parent_id is not None:
            post_proxy = getattr(proxy, post_doc.parent_id)
            post_doc = post_proxy.getContent()
        return post_doc

    security.declarePublic('belongsToLockedThread')
    def belongsToLockedThread(self, post, proxy=None):
        """Is a post in a locked thread"""

        root_post = self.getRootPost(post.id, proxy=proxy)
        return root_post.getContent().id in self.locked_threads

    security.declareProtected(ForumModerate, 'toggleThreadsLockStatus')
    def toggleThreadsLockStatus(self, post_ids=[], proxy=None):
        """lock/unlock threads

        Depends on current lock status for each thread"""
        root_post_ids = []
        # first get a list of all root posts, removing duplicates
        # (in case user selected several posts in the same thread)
        for post_id in post_ids:
            root_post_id = self.getRootPost(post_id, proxy=proxy).id
            if root_post_id not in root_post_ids:
                root_post_ids.append(root_post_id)
        for root_post_id in root_post_ids:
            self.changeThreadLockStatus(root_post_id,
                                        lock=root_post_id in self.locked_threads)

    security.declarePrivate('changeThreadLockStatus')
    def changeThreadLockStatus(self, root_post_id, lock=0):
        """(un)lock a thread"""

        #By adding/removing the root post from the list of locked threads
        if lock:
            self.locked_threads.remove(root_post_id)
        else:
            self.locked_threads.append(root_post_id)


    security.declarePublic('getModerators')
    def getModerators(self, proxy):
        """Get moderators of this forum"""

        pmtool = getToolByName(self, 'portal_membership')
        # filtering on role instead of permission as we are interested
        # in users who have explicit moderator role assigned to them only
        moderators = [k for k,v in pmtool.getMergedLocalRoles(proxy).items()
                      if k.startswith('user:') and 'ForumModerator' in v]
        return moderators

    security.declarePublic('anonymousPostsAllowed')
    def anonymousPostsAllowed(self):
        return self.allow_anon_posts

    security.declarePublic('isFrozen')
    def isFrozen(self):
        return self.frozen_forum
