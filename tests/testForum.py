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

        # Test skins
        forum.forum_view()
        forum.forum_post_form()
        forum.forum_edit_form()

        forum.forum_localrole_form()
        self.portal.REQUEST.role_submit = 1
        forum.forum_localrole_form()

        forum.getPosterName('author')
        forum['forum_icon.gif']

        self.assertEquals(forum.moderation_mode, 1)
        self.assertEquals(forum.getThreads(), [])

    def testEditForum(self):
        forum = self.forum
        forum.editForumProperties(title="new title", 
            description="new description", moderation_mode=0)
        self.assertEquals(forum.title, "new title")
        self.assertEquals(forum.description, "new description")
        self.assertEquals(forum.moderation_mode, 0)

    def testModerators(self):
        forum = self.forum
        self.assertEquals(forum.getModerators(forum), [])
        self.assertEquals(forum.getOfficialModerators(forum), [])

        pmtool = forum.portal_membership
        pmtool.setLocalRoles(forum, member_ids=['root'], 
            member_role='ForumModerator')
        self.assertEquals(forum.getModerators(forum), ['root'])
        self.assertEquals(forum.getOfficialModerators(forum), [{
            'id': 'root', 
            'homedir': 
                '/portal/directory_getentry?dirname=members&entry_id=root', 
            'fullname': 'root'}])


    def testPostCreation1(self):
        # Create new post using skin method.
        forum = self.forum
        post_id = forum.forum_post(subject='subject', message='message',
            author='author')

        self.assertEquals(len(forum.getThreads()), 1)

        forum.forum_view()
        forum.forum_view(post_id)
        forum.forum_post_reply(parent_id=post_id)

        post = forum[post_id]
        self.assertEquals(post['id'], post_id)
        self.assertEquals(post['subject'], "subject")
        self.assertEquals(post['author'], "author")
        self.assertEquals(post['message'], "message")
        self.assertEquals(post['parent_id'], None)
        self.assertEquals(post['published'], 0)
        self.assert_(post['modified'])

        # Publish / unpublish
        forum.forum_publish_posts((post_id,))
        post = forum[post_id]
        self.assertEquals(post['published'], 1)
        forum.forum_unpublish_posts((post_id,))
        post = forum[post_id]
        self.assertEquals(post['published'], 0)

        forum.forum_del_posts((post_id,))
        self.assertEquals(forum.getThreads(), [])


    def testPostCreation2(self):
        # Create / modify post using method calls on the Forum object.
        forum = self.forum
        post_id = forum.addPost(subject='subject', message='message',
            author='author')
        self.assertEquals(len(forum.getThreads()), 1)

        forum.publishPost(post_id, 1)
        post = forum[post_id]
        self.assertEquals(post['published'], 1)

        forum.publishPost(post_id, 0)
        post = forum[post_id]
        self.assertEquals(post['published'], 0)

        forum.delPost(post_id)
        self.assertEquals(forum.getThreads(), [])

    def testThread(self):
        forum = self.forum
        post1_id = forum.addPost(subject='subject1', message='message1',
            author='author1')
        self.assertEquals(len(forum.getThreads()), 1)

        post2_id = forum.addPost(subject='subject2', message='message2',
            author='author2', parent_id=post1_id)
        self.assertEquals(len(forum.getThreads()), 1)

        self.assertEquals(len(forum.getPostReplies(post1_id)), 1)
        self.assertEquals(len(forum.getPostReplies(post2_id)), 0)

        forum.forum_view()
        forum.forum_view(post1_id)
        forum.forum_view(post2_id)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestForum))
    return suite

