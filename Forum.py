import time
import string

from zLOG import LOG, DEBUG, ERROR

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, AddPortalContent, \
        ModifyPortalContent, ManageProperties, ChangePermissions
from Products.NuxUserGroups.CatalogToolWithGroups import mergedLocalRoles
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder
from Products.CPSCore.CPSBase import CPSBaseFolder

from Post import Post

factory_type_information = (
        { 'id': 'Forum',
        'meta_type': 'CPSForum',
        'description': "Forums hold threaded discussions",
        'icon': 'forum_icon.gif',
        'title': "L_forum forum",
        'product': 'CPSForum',
        'factory': 'addCPSForum',
        'filter_content_types': 1,
        'allowed_content_types': ('Post',),
        'immediate_view': 'forum_view',
        'actions': (
            {
            'id': 'view',
            'name': 'L_forum action view',
            'action': 'forum_view',
            'permissions': (View,),
            },
             {'id': 'create',
              'name': 'L_forum action create',
              'action': 'forum_create_form',
              'visible': 0,
              'permissions': ('',)},
            {
            'id': 'edit',
            'name': 'L_forum action modify',
            'action': 'forum_edit_form',
            'permissions': (ManageProperties,),
            }, 
             {
            'id': 'post',
            'name': 'L_action forum post',
            'action': 'forum_post_form',
            'permissions': (AddPortalContent,),
            }, {
            'id': 'localroles',
            'name': 'L_workspace gestion des droits',
            'action': 'folder_localrole_form',
            'permissions': (ChangePermissions,),
            }, {'id': 'isfunctionalobject',
                'name': 'isfunctionalobject',
                'action': 'isfunctionalobject',
                'visible': 0,
                'permissions': ('',),
            }, {'id': 'isproxytype',
                'name': 'isproxytype',
                'action': 'document',
                'visible': 0,
                'permissions': ('',),
            }, {'id': 'issearchabledocument',
                'name': 'issearchabledocument',
                'action': 'issearchabledocument',
                'visible': 0,
                'permissions': ('',),
            },
        ), },
    )

def addDiscussionItem(self, id, title, description, text_format, text,
                      reply_to, RESPONSE=None):
    """
    Add a discussion item
    """
    raise "DISCUSSION", str((id, title, description, text_format, text,
        reply_to, RESPONSE))


def addCPSForum(self, id, **kw):
    """
    Adds a Forum
    """
    forum = CPSForum(id, **kw)
    self.moderation_mode = kw.get('moderation_mode', 1)
    CPSBase_adder(self,forum)

class CPSForum(CPSBaseDocument):
    """
    Forum CPS
    """
    meta_type='CPSForum'
    portal_type='CPSForum'
    allow_discussion = 1
    moderation_mode = 1 # after publishing post
    moderators = []
    security = ClassSecurityInfo()

    def __init__(self, id, **kw):
        """
        constructor
        """
        CPSBaseDocument.__init__(self,id, **kw)

    def getThreads(self):
        """
        returns: tuple of root Posts
        """
        result = [ self.getPostInfo(post) for post in
                self.portal_discussion.getDiscussionFor(self).getReplies()
                if post.in_reply_to is None ]
        return result


    def getPostInfo(self, post):
        """
        returns: tuple of root Posts
        """
        # NB: It looks like we're obliged to maintain
        # our own 'publication state' for the post,
        # but it should be hidden behind a WF
        # on the portal type
        #
        # ... provided the Post has been
        # chosen to effectively be a Portal type,
        # which dosen't apply here
        #
        return {'id':post.id, 'subject':post.title, 'author':post.creator,
                'message':post.text, 'parent_id':post.in_reply_to,
                'published':hasattr(post,'inforum') and post.inforum,
                'modified':post.bobobase_modification_time(),
               }

    def addForumPost(self, id, **kw):
        """
        Adds a post
        """
        discussion = self.portal_discussion.getDiscussionFor(self)

        post_id = discussion.createReply(
               kw['subject'], kw['message'],kw['author'])
        post = discussion.getReply(post_id)
        parent_id = kw.get('parent_id', None)
        post.in_reply_to = parent_id

        self.publishPost(post_id, not self.moderation_mode)

        return post_id

    def delForumPost(self, id):
        """
        Adds a post
        """
        self.portal_discussion.getDiscussionFor(self).deleteReply(id)

    def publishPost(self, id, state=1):
        """
        Publish posts
        """
        post = self.portal_discussion.getDiscussionFor(self).getReply(id)
        post.inforum = state

    def __getitem__(self, id):
        """
        Fetches a post
        """
        try:
            disc = self.portal_discussion.getDiscussionFor(self)
            reply = disc.getReply(id)
            result = self.getPostInfo(reply)
        except AttributeError:
            return None

        return result

    def getPostReplies(self, post_id):
        """
        Fetches post replies
        """
        discussion = self.portal_discussion.getDiscussionFor(self)
        result = [ self.getPostInfo(post) for post in
                discussion.objectValues() if post.in_reply_to == post_id ]
        return result

    def getThreadInfo(self, post_id):
        """ getThreadInfo """
        post = self[post_id]
        while post['parent_id']:
            post = self[post['parent_id']]
            # raise "DEBUG", "parent is "+post

        return post

    def getDescendants(self, post_id, info_getter=None):
        """
        Fetches post tree
        """
        if not info_getter:
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


    def editForumProperties(self,**kw):
        """
        Sets up forum properties
        """
        #self.title = kw.get('title', self.title)
        #self.description = kw.get('description', self.description)

        CPSBaseDocument.edit(self,**kw)
        self.moderation_mode = kw.get('moderation_mode', 1)
        self.moderators = kw.get('moderators', [])


    def getEverything(self):
        """
        Fetches everything (DEBUG)
        """
        discussion = self.portal_discussion.getDiscussionFor(self)
        return [ self.getPostInfo(post) for post in discussion.objectValues() ]

    security.declarePublic('getModerators')
    def getModerators(self, proxy):
        all = mergedLocalRoles(proxy)
        result = []
        for user in all.keys():
            if 'Reviewer' in all[user]:
                result.append(user)
        return result

    security.declarePublic('getOfficialModerators')
    def getOfficialModerators(self, proxy):
        mtool = getToolByName(self, 'portal_membership')
        dtool = getToolByName(self, 'portal_metadirectories').members
        portal_url = getToolByName(self, 'portal_url').getPortalPath()
        dtool_entry_url = "%s/directory_view?dirname=%s&entry_id=" % (portal_url, dtool.id)

        result = []
        for moderator in self.moderators:
            mdata = {'id': moderator}
            mdata['fullname'] = dtool.getEntry(moderator)[dtool.display_prop] or moderator
            mdata['homedir'] = dtool_entry_url + moderator
            result.append(mdata)
        return result

def addCPSPost(self, id, RESPONSE=None, **kw):
    """function addCPSPost

    title: string      the subject
    author: string     the author
    message: string    the *structured text mix* message
    forum_id: string   the parent forum id
    parent_id: string  an optional parent Post uid, as obtained from
        parentPost.getPostUID()
    """
    post = CPSPost(id, **kw)
    post.parent_id = kw['parent_id']
    if post.parent_id is None:
        post.parent_id = '_FORUM_'
    self._setObject(id, post)


class CPSPost(CPSBaseDocument, Post):
    """Class Post for CPS
    """
    # Attributes:
    meta_type = "CPSPost"
    forum_meta_type = 'CPSForum'
    _properties = CPSBaseDocument._properties + (
        { 'id': 'text', 'type': 'string', 'mode': 'w', 'label': 'Post author' },
        { 'id': 'author', 'type': 'string', 'mode': 'w', 'label': 'Post author' },
        { 'id': 'forum_id', 'type': 'string', 'mode': 'w', 'label': 'Parent Forum id' },
        { 'id': 'parent_id', 'type': 'string', 'mode': 'w', 'label': 'Parent Post id' },
        )

    def getPostInfo(self):
        """function getPostInfo

        returns tuple (url, subject, author)
        """
        return (self.getId(), self.getSubject(), self.getAuthor())

    def __init__(self, id, **kw):
        """constructor
        """
        CPSBaseDocument.__init__(self, id, **kw)


