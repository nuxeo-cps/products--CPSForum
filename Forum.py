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
        'permissions': ('Modify Folder Properties',),
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
    self.allow_anon_posts = kw.get('allow_anon_posts', 0)
    self.send_moderation_notification = kw.get('send_moderation_notification', 0)
    self.frozen_forum = kw.get('frozen_forum', 0)
    CPSBase_adder(self, forum)


class CPSForum(CPSBaseDocument):
    """
    CPS Forum definition
    """
    meta_type = 'CPSForum'
    portal_type = 'CPSForum'
    # XXX: is it needed ?
    allow_discussion = 1
    #moderation_mode: 1=a priori, 0=a posteriori
    moderation_mode = 1
    allow_anon_posts = 0
    send_moderation_notification = 0
    #if frozen, no longer possible to post messages
    frozen_forum = 0
    moderators = []
    security = ClassSecurityInfo()

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

    security.declareProtected(View, 'changePostPublicationStatus')
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

    security.declareProtected('Modify Folder Properties', 'editForumProperties')
    def editForumProperties(self, **kw):
        """Edit forum properties
        """

        CPSBaseDocument.edit(self,**kw)
        self.moderation_mode = kw.get('moderation_mode', 1)
        self.allow_anon_posts = kw.get('allow_anon_posts', 0)
        self.send_moderation_notification = kw.get('send_moderation_notification', 0)
        self.frozen_forum = kw.get('frozen_forum', 0)
        self.moderators = kw.get('moderators', [])

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
        
        def reduce_eq(func,seq,init=None):
            if init is None: init, seq = seq[0], seq[1:]
            for item in seq: init = func(init,item)
            return init
        
        return reduce_eq(lambda line, word, width=width: '%s%s%s' %
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
            #XXX: this has to be i18n-ed
            subject = "Soumission d'un message sur le Forum %s" % self.title
            post_url = proxy.absolute_url() + '?post_id=' + post_id
            body = "Un nouveau message à modérer vient d'être poste sur le forum %s.\n\nCe message peut être consulte à l'adresse suivante:\n%s" % (self.title, post_url)
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
            content = content % (
                from_address, reply_to, ', '.join(mto), subject,
                content_type, charset, body)
            
            mailhost.send(content, mto=mto, mfrom=from_address,
                          subject=subject, encode='8bit')

