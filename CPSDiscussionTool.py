from zLOG import LOG, DEBUG

from Globals import PersistentMapping
from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CMFDefault.DiscussionItem import DiscussionItemContainer
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem

class CPS3DiscussionContainer(SimpleItem, DiscussionItemContainer):
    meta_type = 'CPS3 Discussion Container'

    def __init__(self, id):
        self.id = id
        self._container = PersistentMapping()

class CPS3DiscussionTool(ObjectManager, DiscussionTool):

    meta_type = 'CPS3 Discussion Tool'
    manage_options = ObjectManager.manage_options + DiscussionTool.manage_options

    def getDiscussionFor(self, content):
        """
            Return the talkback for content, creating it if need be.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        if hasattr(content, 'getDocid'):
            docid = content.getDocid()
        else:
            docid = content.getId()
        discussion = self._getOb(docid, None)
        if not discussion:
            discussion = self._createDiscussionFor( content )
            LOG('CPS3DiscussionTool', DEBUG, 'New discussion created for %s' % \
                content.getId())

        LOG('CPS3DiscussionTool', DEBUG, 'Found discussion for %s' % \
                content.getId(), str(discussion) + '\n')
        return discussion

    def _createDiscussionFor( self, content ):
        """
            Create the object that holds discussion items inside
            the object being discussed, if allowed.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        newid = content.getId()
        discussion = CPS3DiscussionContainer(newid)
        self._setObject(newid, discussion)
        return discussion
