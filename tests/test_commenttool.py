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
        self.sc = self.portal.sections

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


    def testGetForum4CommentsWorkspaces(self):
        doc_url = self.proxy_doc.absolute_url(relative=1)

        self.assertEqual(self.pd.getCommentForumURL(doc_url), '')

        self.assertEqual(self.pd.isCommentingAllowedFor(self.proxy_doc), 0)

        parent_folder = self.proxy_doc.aq_inner.aq_parent
        self.assert_('.cps_discussions' not in parent_folder.objectIds())

        forum = self.pd.getForum4Comments(self.proxy_doc)

        # Check that .cps_discussions is created one level up from
        # the proxy_doc
        self.assert_('.cps_discussions' in parent_folder.objectIds())

        # As we work under Workspaces check that portal_type of
        # .cps_discussions is 'Workspace'
        discussions_folder = getattr(parent_folder, '.cps_discussions')
        self.assertEqual(discussions_folder.portal_type, 'Workspace')

        # CPSForum should be created under .cps_discussions
        self.assertEqual(getattr(discussions_folder, forum.getId()).portal_type,
                         'CPSForum')

        # .cps_workflow_configuration should be created under .cps_discussions
        discussions_folder_ids = discussions_folder.objectIds()
        self.assert_('.cps_workflow_configuration' in discussions_folder_ids)

        # Check that under Workspaces placeful workflow chain for CPSForum
        # is set to 'workspace_forum_wf'
        wfc = getattr(discussions_folder, '.cps_workflow_configuration')
        self.assertEqual(wfc.getPlacefulChainFor('CPSForum')[0],
                         'workspace_forum_wf')

        self.assertEqual(wfc.getPlacefulChainFor('ForumPost')[0],
                         'forum_post_wf')

        forum_url = forum.absolute_url(relative=1)
        self.assertEqual(self.pd.getCommentForumURL(doc_url), forum_url)

        self.assertEqual(self.pd.getCommentedDocument(forum_url), doc_url)

        self.assertEqual(self.pd.isCommentingAllowedFor(self.proxy_doc), 1)


    def testGetForum4CommentsSections(self):
        # Create 'Chat' object as it's allowed to create it under Sections
        # by default
        self.portal.portal_workflow.invokeFactoryFor(self.sc, 'Chat', 'chat')
        sc_proxy_doc = getattr(self.sc, 'chat')

        doc_url = sc_proxy_doc.absolute_url(relative=1)

        self.assertEqual(self.pd.getCommentForumURL(doc_url), '')

        self.assertEqual(self.pd.isCommentingAllowedFor(sc_proxy_doc), 0)

        parent_folder = sc_proxy_doc.aq_inner.aq_parent
        self.assert_('.cps_discussions' not in parent_folder.objectIds())

        forum = self.pd.getForum4Comments(sc_proxy_doc)

        # Check that .cps_discussions is created one level up from
        # the proxy_doc
        self.assert_('.cps_discussions' in parent_folder.objectIds())

        # As we work under Sections check that portal_type of
        # .cps_discussions is 'Section'
        discussions_folder = getattr(parent_folder, '.cps_discussions')
        self.assertEqual(discussions_folder.portal_type, 'Section')

        # CPSForum should be created under .cps_discussions
        self.assertEqual(getattr(discussions_folder, forum.getId()).portal_type,
                         'CPSForum')

        # .cps_workflow_configuration should be created under .cps_discussions
        discussions_folder_ids = discussions_folder.objectIds()
        self.assert_('.cps_workflow_configuration' in discussions_folder_ids)

        # Check that under Sections placeful workflow chain for CPSForum
        # is set to 'section_forum_wf'
        wfc = getattr(discussions_folder, '.cps_workflow_configuration')
        self.assertEqual(wfc.getPlacefulChainFor('CPSForum')[0],
                         'section_forum_wf')

        self.assertEqual(wfc.getPlacefulChainFor('ForumPost')[0],
                         'forum_post_wf')

        forum_url = forum.absolute_url(relative=1)
        self.assertEqual(self.pd.getCommentForumURL(doc_url), forum_url)

        self.assertEqual(self.pd.getCommentedDocument(forum_url), doc_url)

        self.assertEqual(self.pd.isCommentingAllowedFor(sc_proxy_doc), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommentTool))
    return suite
