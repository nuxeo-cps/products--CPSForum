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
        self.logout()


    def testGetCommentForumURL(self):
        proxy_forum, forum = self._createForum()
        news_url = self.proxy_doc.absolute_url(relative=1)

        self.assertEqual(self.pd.getCommentForumURL(news_url), '')

        forum_url = proxy_forum.absolute_url(relative=1)
        self.pd._data[news_url] = forum_url
        self.assertEqual(self.pd.getCommentForumURL(news_url), forum_url)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommentTool))
    return suite
