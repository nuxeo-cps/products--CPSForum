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
        forum_id = 'forum'
        self.login('root')
        self.ws = self.portal.workspaces

        self.portal.portal_workflow.invokeFactoryFor(self.ws, 'CPSForum', forum_id)
        self.proxy_forum = getattr(self.ws, forum_id)
        self.forum = self.proxy_forum.getContent()

        mdir = self.portal.portal_directories.members
        mdir.createEntry({'id': 'author'})
        mdir.createEntry({'id': 'author1'})
        mdir.createEntry({'id': 'author2'})

    def beforeTearDown(self):
        self.logout()

    def testDiscussionTool(self):
        pd = self.portal.portal_discussion
        self.assertEquals(pd.meta_type, "CPS Discussion Tool")
        self.assert_(pd.manage_overview)

    def testEmptyForum(self):
        forum = self.forum
        proxy_forum = self.proxy_forum
        # Test skins
        proxy_forum.forum_view()
        proxy_forum.forum_post_form()
        proxy_forum.forum_edit_form()

        proxy_forum.forum_localrole_form()
        self.portal.REQUEST.role_submit = 1
        proxy_forum.forum_localrole_form()

        forum.getPosterName('author')

        self.assertEquals(forum.moderation_mode, 1)
        self.assertEquals(forum.getThreads(proxy=proxy_forum), [])

    def testEditForum(self):
        forum = self.forum
        forum.edit(Title="new title", Description="new description",
                   moderation_mode=0)
        self.assertEquals(forum.Title(), "new title")
        self.assertEquals(forum.Description(), "new description")
        self.assertEquals(forum.moderation_mode, 0)

    def testPostCreation1(self):
        # Create new post using skin method.
        forum = self.forum
        proxy_forum = self.proxy_forum
        self.assertEquals(forum.moderation_mode, 1)
        post_id = proxy_forum.forum_post(subject='subject', message='message',
                                         author='root')

        self.assertEquals(len(forum.getThreads(proxy=proxy_forum)), 1)

        forum.forum_view()
        forum.forum_view(post_id)
        proxy_forum.forum_post_reply(parent_id=post_id)
        
        post_proxy = getattr(proxy_forum, post_id)
        post_info = forum.getPostInfo(post_proxy)
        self.assertEquals(post_info['id'], post_id)
        self.assertEquals(post_info['subject'], "subject")
        self.assertEquals(post_info['author'], "root")
        self.assertEquals(post_info['message'], "message")
        self.assertEquals(post_info['parent_id'], None)
        self.assertEquals(post_info['published'], 0)
        self.assertEquals(post_info['locked'], 0)
        self.assert_(post_info['modified'])

        # Publish / unpublish
        proxy_forum.forum_publish_posts(forum_thread_ids=(post_id,))
        post_info = forum.getPostInfo(post_proxy)
        self.assertEquals(post_info['published'], 1)
        proxy_forum.forum_unpublish_posts(forum_thread_ids=(post_id,))
        post_info = forum.getPostInfo(post_proxy)
        self.assertEquals(post_info['published'], 0)

        proxy_forum.forum_del_posts(forum_thread_ids=(post_id,))
        self.assertEquals(forum.getThreads(proxy=proxy_forum), [])

    def testPostCreation2(self):
        # Create new post using skin method.
        forum = self.forum
        proxy_forum = self.proxy_forum
        forum.edit(moderation_mode=0)
        self.assertEquals(forum.moderation_mode, 0)
        post_id = proxy_forum.forum_post(subject='subject', message='message',
                                         author='root')

        self.assertEquals(len(forum.getThreads(proxy=proxy_forum)), 1)

        forum.forum_view()
        forum.forum_view(post_id)
        
        post_proxy = getattr(proxy_forum, post_id)
        post_info = forum.getPostInfo(post_proxy)
        self.assertEquals(post_info['id'], post_id)
        self.assertEquals(post_info['subject'], "subject")
        self.assertEquals(post_info['author'], "root")
        self.assertEquals(post_info['message'], "message")
        self.assertEquals(post_info['parent_id'], None)
        self.assertEquals(post_info['published'], 1)
        self.assertEquals(post_info['locked'], 0)
        self.assert_(post_info['modified'])

        # Publish / unpublish
        proxy_forum.forum_unpublish_posts(forum_thread_ids=(post_id,))
        post_info = forum.getPostInfo(post_proxy)
        self.assertEquals(post_info['published'], 0)

    def testThread(self):
        forum = self.forum
        proxy_forum = self.proxy_forum
        forum.edit(moderation_mode=0)
        self.assertEquals(forum.moderation_mode, 0)

        post1_id = proxy_forum.forum_post(subject='subject1',
                                          message='message1',
                                          author='root')
        self.assertEquals(len(forum.getThreads(proxy=proxy_forum)), 1)

        post2_id = proxy_forum.forum_post(subject='subject1 reply',
                                          message='message1 reply',
                                          author='root',
                                          parent_id=post1_id)
        self.assertEquals(len(forum.getThreads(proxy=proxy_forum)), 1)

        post3_id = proxy_forum.forum_post(subject='subject2',
                                          message='message2',
                                          author='root')
        self.assertEquals(len(forum.getThreads(proxy=proxy_forum)), 2)

        self.assertEquals(len(forum.getDescendants(post1_id, proxy=proxy_forum)), 1)
        self.assertEquals(len(forum.getDescendants(post2_id, proxy=proxy_forum)), 0)
        self.assertEquals(len(forum.getDescendants(post3_id, proxy=proxy_forum)), 0)

        forum.forum_view()
        forum.forum_view(post1_id)
        forum.forum_view(post2_id)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestForum))
    return suite
