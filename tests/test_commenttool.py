# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSForumTestCase


class TestCommentTool(CPSForumTestCase.CPSForumTestCase):

    def afterSetUp(self):
        self.login('manager')
        self.ws = self.portal.workspaces

        self.portal.portal_workflow.invokeFactoryFor(self.ws, 'News', 'news')
        self.proxy_doc = getattr(self.ws, 'news')
        self.doc = self.proxy_doc.getContent()

        self.pd = self.portal.portal_discussion


    def _createForum(self):
        forum_id = 'forum'
        self.portal.portal_workflow.invokeFactoryFor(self.ws, 'CPSForum',
                                                     forum_id)
        proxy_forum = getattr(self.ws, forum_id)
        forum = proxy_forum.getContent()
        return (proxy_forum, forum)


    def beforeTearDown(self):
        data = self.pd._data
        data.clear()
        self.pd._data = data
        self.logout()


    def testGetCommentForumURL(self):
        proxy_forum, forum = self._createForum()
        news_url = self.proxy_doc.absolute_url(relative=1)

        self.assertEqual(self.pd.getCommentForumURL(news_url), '')

        forum_url = proxy_forum.absolute_url(relative=1)
        self.pd._data[news_url] = forum_url
        self.assertEqual(self.pd.getCommentForumURL(news_url), forum_url)


    def testGetCommentedDocument(self):
        proxy_forum, forum = self._createForum()
        news_url = self.proxy_doc.absolute_url(relative=1)
        forum_url = proxy_forum.absolute_url(relative=1)

        self.assert_(self.pd.getCommentedDocument(forum_url) is None)

        self.pd._data[news_url] = forum_url
        self.assertEqual(self.pd.getCommentedDocument(forum_url), news_url)


    def testRegisterCommentForum(self):
        proxy_forum, forum = self._createForum()
        news_url = self.proxy_doc.absolute_url(relative=1)
        forum_url = proxy_forum.absolute_url(relative=1)

        self.assertEqual(len(self.pd._data.keys()), 0)

        # test default parameters
        self.pd.registerCommentForum()
        self.assertEqual(len(self.pd._data.keys()), 1)
        self.assertEqual(self.pd._data[''], '')

        self.pd.registerCommentForum(proxy_path=news_url, forum_path=forum_url)
        self.assertEqual(len(self.pd._data.keys()), 2)
        self.assertEqual(self.pd._data[news_url], forum_url)


    def testIsCommentingAllowedFor(self):
        self.assertEqual(self.pd.isCommentingAllowedFor(self.proxy_doc), 0)

        proxy_forum, forum = self._createForum()
        news_url = self.proxy_doc.absolute_url(relative=1)
        forum_url = proxy_forum.absolute_url(relative=1)
        self.pd._data[news_url] = forum_url
        self.assertEqual(self.pd.isCommentingAllowedFor(self.proxy_doc), 1)


    def testSetAllowDiscussion(self):
        doc = self.proxy_doc.getContent()
        self.assertEqual(doc.allow_discussion, 0)

        self.pd.setAllowDiscussion(self.proxy_doc, 1)
        self.assertEqual(doc.allow_discussion, 1)

        self.pd.setAllowDiscussion(self.proxy_doc, 0)
        self.assertEqual(doc.allow_discussion, 0)


    def testCreateAnonymousForumPost(self):
        proxy_forum, forum = self._createForum()
        post_id = 'post1'
        subject = 'subject'
        author = 'anonymous'
        message = 'message'
        parent_id = None

        self.assertEqual(len(proxy_forum.objectIds()), 0)

        self.logout()
        self.pd.createAnonymousForumPost(proxy_forum, post_id, subject,
                                         author, message, parent_id)

        self.assertEqual(len(proxy_forum.objectIds()), 1)
        self.assert_(hasattr(proxy_forum, post_id))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommentTool))
    return suite
