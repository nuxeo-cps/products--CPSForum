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

    def testEmptyForum(self):
        forum = self.forum
        forum.forum_view()

        self.assertEquals(forum.moderation_mode, 1)
        self.assertEquals(forum.getThreads(), [])

    def testEditForum(self):
        forum = self.forum
        forum.editForumProperties(title="new title", 
            description="new description", moderation_mode=0)
        self.assertEquals(forum.title, "new title")
        self.assertEquals(forum.description, "new description")
        self.assertEquals(forum.moderation_mode, 0)


    def testPostCreation1(self):
        # Create new post using skin method.
        forum = self.forum
        post_id = forum.forum_post(subject='subject', message='message',
            author='author')

        self.assertEquals(len(forum.getThreads()), 1)

        forum.forum_view()
        forum.forum_view(post_id)

        post = forum[post_id]
        self.assertEquals(post['id'], post_id)
        self.assertEquals(post['subject'], "subject")
        self.assertEquals(post['author'], "author")
        self.assertEquals(post['message'], "message")
        self.assertEquals(post['parent_id'], None)
        self.assertEquals(post['published'], 0)
        self.assert_(post['modified'])

        forum.publishPost(post_id, 1)
        post = forum[post_id]
        self.assertEquals(post['published'], 1)

        forum.publishPost(post_id, 0)
        post = forum[post_id]
        self.assertEquals(post['published'], 0)

        # getModerators / getOfficialModerators need a proxy so we put the
        # test here
        # self.assertEquals(forum.getModerators(post), [])
        # self.assertEquals(forum.getOfficialModerators(post), [])

        forum.forum_del_posts((post_id,))
        self.assertEquals(forum.getThreads(), [])


    def testPostCreation2(self):
        # Create post using method calls on the Forum object.
        forum = self.forum
        post_id = forum.addPost(subject='subject', message='message',
            author='author')
        self.assertEquals(len(forum.getThreads()), 1)

        forum.delPost(post_id)
        self.assertEquals(forum.getThreads(), [])



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestForum))
    return suite

