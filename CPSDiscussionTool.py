from zLOG import LOG, DEBUG

from Globals import PersistentMapping
from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CMFDefault.DiscussionItem import DiscussionItemContainer
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem

class CPSDiscussionContainer(SimpleItem, DiscussionItemContainer):
    meta_type = 'CPS Discussion Container'

    def __init__(self, id):
        self.id = id
        self._container = PersistentMapping()

class CPSDiscussionTool(ObjectManager, DiscussionTool):

    meta_type = 'CPS Discussion Tool'
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
            LOG('CPSDiscussionTool', DEBUG, 'New discussion created for %s' % \
                content.getId())

        LOG('CPSDiscussionTool', DEBUG, 'Found discussion for %s' % \
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
        discussion = CPSDiscussionContainer(newid)
        self._setObject(newid, discussion)
        return discussion
