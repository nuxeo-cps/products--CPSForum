$Id$

--------------------------------------------------
About CPSForum - Installation procedure
--------------------------------------------------

--------------------------------------------------
HOW TO INSTALL
--------------------------------------------------

- Requirements: the CMF Discussion tool (portal_discussion) must be
  installed in the portal

- Copy CPSForum into your zope/Products directory

- The remainder of the installation process is straightforward, as it 
  consists in executing the product's installer (as you would for any other
  product).

- From the ZMI, go to the CPS root, instanciate an External Method with the
  following parameters:
  ID = any Id you want, like cpsforuminstaller
  Title = anything you want, like CPSForum Installer
  Module Name = CPSForum.install
  Function Name = install

- Execute the script by going to the Test tab. This should automatically create
  a CPSForum entry in portal_types. 