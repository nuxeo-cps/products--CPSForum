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

# Imports CMF
from Products.CMFCore.CMFCorePermissions import ManageProperties
from Products.CMFCore.utils import getToolByName

# Imports Zope
from AccessControl import ClassSecurityInfo
from zLOG import LOG, INFO

def addPost(self, id, **kw):
    """function addPost
    """
    if not kw.has_key("post"):
        raise KeyError(
            "No 'Post' instance was submitted for this Post creation in " +
            str(kw))

    self._setObject(id, kw['post'])
    if hasattr(kw, "REQUEST"):
        return self.manage_main(self, kw['REQUEST'])

    return None


class Post:
    """Class Post
    """
    # Attributes:
    author = None
    attachment = None
    forum_id = None
    parent_id = '_FORUM_'

    meta_type = 'Post'
    forum_meta_type = 'Forum'

    security = ClassSecurityInfo()

    # Operations
    def getSubject(self):
        """function getSubject

        returns: string the subject
        """
        return self.title

    getTitle = getSubject

    security.declareProtected(ManageProperties, 'setSubject')
    def setSubject(self, subject=None):
        """function setSubject

        subject: string the subject
        """
        if not subject:
            subject = self.getId()

        self.title = subject

    setTitle = setSubject

    def getAuthor(self):
        """function getAuthor

        returns: string the author
        """
        if self.author:
            return self.author

        return self.Creator()

    security.declareProtected(ManageProperties, 'setAuthor')
    def setAuthor(self, member_id=None):
        """function setAuthor

        author: string the author *member id*
        """
        pm = getToolByName(self, "portal_membership")

        member = pm.getAuthenticatedMember()
        if member_id:
            member = pm.getMemberById(member_id)

        # when self.author is None,
        #  getAuthor is in charge of
        #  returning self.Creator()
        self.author = member

    def getMessage(self):
        """function getMessage

        returns: string the *html cooked* message
        """
        return self.text

    def getAttachment(self):
        """function getAttachment

        returns None
        """
        return self.attachment

    security.declareProtected(ManageProperties, 'setMessage')
    def setMessage(self, message):
        """function setMessage

        message: string the *structured text mix* message
        """
        # should be moved in cmf
        self.edit(text_format='structured_text', text=message)

    def getPostUID(self):
        """function getPostUID

        NEARLY UNUSED - shall disappear
        making unique ids in zope ids
        in general is the rule

        returns string a *unique identifier* through
                       all posts in the same forum
        """
        if not hasattr(self, "_uid"):
            self._uid = self.getId() + "_" + self.bobobase_modification_time()

        return self._uid

    def getPostInfo(self):
        """function getPostInfo

        returns tuple (url, subject, author)
        """
        return (self.absolute_url(), self.getSubject(), self.getAuthor())

    def getReplies(self):
        """function getPostReplies

        post: the parent Post

        returns tuple Brains of Post
        """
        return self.getForum().getPostReplies(self)


    def getForum(self):
        """function getForum

        returns: Forum the parent forum
        """
        query = {}
        query["meta_type"] = self.forum_meta_type
        query["id"] = self.forum_id
        results = getToolByName(self, "portal_catalog").searchResults(REQUEST=query)
        if len(results):
            return results[0].getObject()
        else:
            raise KeyError, "No Forum with id = [%s] exists. Post '%s' is orphan." % (
                    self.forum_id,
                    self.getId(),
                )

    def __repr__(self):
        return "<Post '%s' at forum '%s', " \
            "{'subject':\"%s\",'author':\"%s\",'message':\"%s...\"}>" % (
                self.getId(),
                self.forum_id,
                self.getSubject(),
                self.getAuthor(),
                self.getMessage()[:16],
            )
