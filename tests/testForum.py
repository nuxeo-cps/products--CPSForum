# TODO: 
# - don't depend on getDocumentSchemas / getDocumentTypes but is there
#   an API for that ?

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSForumTestCase


class TestForum(CPSForumTestCase.CPSForumTestCase):

    def afterSetUp(self):
        self.login('root')
        self.ws = self.portal.workspaces
        self.ws.invokeFactory('CPSForum', 'forum')
        self.forum = self.ws.forum

    def beforeTearDown(self):
        self.logout()

    def testDiscussionTool(self):
        pd = self.portal.portal_discussion
        self.assertEquals(pd.meta_type, "CPS Discussion Tool")
        self.assert_(pd.manage_overview)

    def testForum(self):
        forum = self.forum

        forum.forum_view()

        post_id = forum.addForumPost(subject='subject', message='message',
            author='author')

        forum.forum_view(post_id)

        post = forum[post_id]
        self.assertEquals(post['subject'], 'subject')
        self.assertEquals(post['message'], 'message')
        self.assertEquals(post['author'], 'author')

        #print forum.getPostInfo(post)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestForum))
    return suite

