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
from Products.CMFCore.CMFCorePermissions import View, ChangePermissions
from Products.CPSCore.CPSBase import CPSBase_adder
try:
    from Products.CPSDocument.CPSDocument import CPSDocument as BaseDocument
except ImportError:
    from Products.CPSCore.CPSBase import CPSBaseDocument as BaseDocument
from CPSForumPermissions import ForumModerate
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
    'cps_proxy_type': 'document',
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
    #if frozen, no longer possible to post messages
    frozen_forum = 0
    moderators = []
    security = ClassSecurityInfo()
    #contains root post ids of locked threads
    locked_threads = []

    security.declareProtected(View, 'getThreads')
    def getThreads(self):
        """Return a list of root posts

        Does not return replies to post, just thread root posts
        """

        discussion = self.portal_discussion.getDiscussionFor(self)
        result = [ self.getPostInfo(post)
                   for post in discussion.getReplies()
                   if post.in_reply_to is None ]
        return result

    security.declareProtected(View, 'getPostInfo')
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
            'locked': post.id in self.locked_threads
        }

    security.declareProtected(View, 'addPost')
    def addPost(self, subject="", message="", author="", parent_id=None,
                proxy=None, comment_mode=0):
        """Add a new post

        Returns the new post's id."""
        if not self.frozen_forum:
            discussion = self.portal_discussion.getDiscussionFor(self)
            post_id = discussion.createReply(subject, message, author)
            post = discussion.getReply(post_id)
            post.in_reply_to = parent_id
            self.changePostPublicationStatus(post_id, not self.moderation_mode)
            if (self.send_moderation_notification and
                self.moderation_mode and not comment_mode):
                self.notifyModerators(post_id=post_id, proxy=proxy)
            return post_id
        else:
            return None

    security.declareProtected(View, 'delPost')
    def delPost(self, id):
        """Delete a post

        The post is refered to by its id"""
        self.portal_discussion.getDiscussionFor(self).deleteReply(id)

    security.declareProtected(ForumModerate, 'changePostPublicationStatus')
    def changePostPublicationStatus(self, id, status=1):
        """(Un)Publish post <id>"""
        post = self.portal_discussion.getDiscussionFor(self).getReply(id)
        # XXX: this breaks encapsulation. Fix this.
        post.inforum = status

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

    security.declareProtected(View, 'getPostReplies')
    def getPostReplies(self, post_id):
        """Return replies to root post

        Root post is refered to by <post_id>"""
        discussion = self.portal_discussion.getDiscussionFor(self)
        # FIXME: is it really the right algorithm ?
        result = [ self.getPostInfo(post)
                   for post in discussion.objectValues()
                   if post.in_reply_to == post_id ]
        return result

    security.declareProtected(View, 'getDescendants')
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

    security.declarePrivate('getRootPost')
    def getRootPost(self, post_id):
        """get the root post of thread post_id belongs to"""

        discussion = self.portal_discussion.getDiscussionFor(self)
        post = discussion.getReply(post_id)
        while post.in_reply_to is not None:
            post = discussion.getReply(post.in_reply_to)
        return post

    security.declarePublic('belongsToLockedThread')
    def belongsToLockedThread(self, post_id):
        """Is a post in a locked thread"""

        root_post = self.getRootPost(post_id)
        return root_post.id in self.locked_threads

    security.declareProtected(ForumModerate, 'toggleThreadsLockStatus')
    def toggleThreadsLockStatus(self, post_ids=[]):
        """lock/unlock threads

        Depends on current lock status for each thread"""
        root_post_ids = []
        # first get a list of all root posts, removing duplicates
        # (in case user selected several posts in the same thread)
        for post_id in post_ids:
            root_post_id = self.getRootPost(post_id).id
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

    security.declarePublic('isSendingModerNotifs')
    def isSendingModerNotifs(self):
        return self.send_moderation_notification

    security.declarePublic('anonymousPostsAllowed')
    def anonymousPostsAllowed(self):
        return self.allow_anon_posts

    security.declarePublic('isFrozen')
    def isFrozen(self):
        return self.frozen_forum

    security.declarePrivate('checkEmails')
    def checkEmails(self,list=[]):
        res = []
        for item in list:
            if item and item not in res:
                res.append(item)
        return res

    security.declarePrivate('textwrap')
    def textwrap(self,text, width):
        """Textwrap function definition, for email formatting

        Wraps text to width
        inspired by MailBoxer's version, using reduce_eq
        as built-in function reduce is not available from
        python scripts"""

        def reduceEq(func, seq, init=None):
            if init is None:
                init, seq = seq[0], seq[1:]
            for item in seq:
                init = func(init, item)
            return init

        return reduceEq(lambda line, word, width=width: '%s%s%s' %
                      (line,
                       ' \n'[(len(line[line.rfind('\n')+1:])
                              + len(word.split('\n',1)[0]
                                    ) >= width)],
                       word),
                      text.split(' ')
                      )

    security.declarePrivate('notifyModerators')
    def notifyModerators(self, post_id=None, proxy=None):
        if post_id and proxy:
            moderators = self.getModerators(proxy)
            members_dir = getToolByName(self, 'portal_directories').members
            moderator_emails = []
            for moderator_id in moderators:
                entry = members_dir.getEntry(moderator_id[5:])
                if entry and entry.has_key('email'):
                    moderator_emails.append(entry['email'])
            checked_emails = self.checkEmails(list=moderator_emails)
            utool = getToolByName(self, 'portal_url')
            portal = utool.getPortalObject()

            mcat = getToolByName(self, 'Localizer').default
            subject_i18n = mcat('forum_mailtitle_new_msg_submitted').encode('ISO-8859-15', 'ignore')
            subject = subject_i18n + self.title
            post_url = proxy.absolute_url() + '?post_id=' + post_id
            body_i18n_1 = mcat('forum_mailbody_new_msg_submitted1').encode('ISO-8859-15', 'ignore')
            body_i18n_2 = mcat('forum_mailbody_new_msg_submitted2').encode('ISO-8859-15', 'ignore')
            body = body_i18n_1 + self.title + '.\n\n' + body_i18n_2 + '\n' + post_url

            if checked_emails:
                self.sendEmail(from_address=getattr(portal,
                                                    'email_from_address'),
                               subject=subject,
                               body=self.textwrap(body, 72),
                               mto=checked_emails)

    security.declarePrivate('sendEmail')
    def sendEmail(self, from_address='nobody@example.com', reply_to=None,
                  subject='No subject', body='No body', content_type='text/plain',
                  charset='ISO-8859-15', mto=None):

        mailhost = getattr(getToolByName(self, 'portal_url').getPortalObject(), 'MailHost')
        if reply_to is None:
            reply_to = from_address

            content = """\
From: %s
Reply-To: %s
To: %s
Subject: %s
Content-Type: %s; charset=%s
Mime-Version: 1.0

%s"""
            content = content % (from_address, reply_to, ', '.join(mto),
                                 subject, content_type, charset, body)

            mailhost.send(content, mto=mto, mfrom=from_address,
                          subject=subject, encode='8bit')
