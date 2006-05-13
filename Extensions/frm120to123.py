# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga <ep@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

"""A script for making forums created with CPSForum 1.2.0-1.2.2
   work with CPSForum 1.2.3 or later

 How to use it:
 - log into the ZMI as manager
 - go to your CPS root directory
 - create an External Method with the following parameters:

     id            : forum_converter (or whatever)
     title         : CPSForum converter (or whatever)
     Module Name   : CPSForum.frm120to123
     Function Name : convert

 - save it
 - click on the test tab of this external method
"""

from Products.CPSInstaller.CPSInstaller import CPSInstaller

# method to convert posts Creator to author
def convertPost(proxy_post, installer):
    installer.log("    Converting post %s" % proxy_post.id)
    post = proxy_post.getEditableContent()
    creator = post.Creator()
    kw = {'author': creator or ''}
    post.edit(**kw)

# method for processing a forum
def convertForum(proxy_forum, installer):
    installer.log("  Processing forum %s" % proxy_forum.id)
    # change permissions on forum
    wf_chain = installer.portal.portal_workflow.getChainFor(proxy_forum)
    if wf_chain[0] == 'section_forum_wf':
        installer.log("    Forum follows section_forum_wf: updating 'Modify portal content' permission")
        proxy_forum.manage_permission('Modify portal content',
                                      ['ForumModerator', 'Manager', 'Owner',
                                       'SectionManager', 'SectionReviewer',
                                       'WorkspaceManager', 'WorkspaceMember'])
        proxy_forum.proxyChanged()
    # process posts
    for proxy_post in proxy_forum.objectValues():
        convertPost(proxy_post, installer)

# recursive descent of hierarchy (Workspace, Section, etc.)
def inspectFolder(proxy_folder, installer, portal_types_to_export):
    installer.log("Searching for forums in %s" %
                  installer.portal.portal_url.getRelativeUrl(proxy_folder))
    for object in proxy_folder.objectValues():
        if object.portal_type == 'CPSForum':
            convertForum(object, installer)
        elif (object.meta_type == 'CPS Proxy Folder' and
              object.portal_type in portal_types_to_export):
            inspectFolder(object, installer, portal_types_to_export)

def convert(self):

    installer = CPSInstaller(self, 'ForumConverter')
    installer.log("Starting conversion")

    # prepare hierarchy descent
    portal_types_to_export = []
    for tree in installer.portal.portal_trees.objectValues():
        for type in tree.getProperty('type_names'):
            if type not in portal_types_to_export:
                portal_types_to_export.append(type)
    installer.log("The following portal types will be considered as folders for the hierarchy recursive descent: %s" % portal_types_to_export)

    for object in installer.portal.objectValues():
        if (object.meta_type == 'CPS Proxy Folder' and
            object.portal_type in portal_types_to_export):
            inspectFolder(object, installer, portal_types_to_export)

    installer.log("End of conversion")
    return installer.logResult()
