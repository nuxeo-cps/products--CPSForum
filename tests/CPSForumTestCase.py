from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('CPSForum')

CPSTestCase.setupPortal()

class CPSForumTestCase(CPSTestCase.CPSTestCase):
    pass


