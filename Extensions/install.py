# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
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

"""
CPSForum Installer

HOWTO USE THAT ?

 - Log into the ZMI as manager
 - Go to your CPS root directory
* - Create an External Method with the following parameters:

     id    : CPSForum Installer (or whatever)
     title : CPSForum Installer (or whatever)
     Module Name   :  CPSForum.install
     Function Name : install

 - save it
 - click now the test tab of this external method.
 - that's it !

"""

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CPSForum.CPSForumPermissions import ForumPost, ForumModerate

def install(self):
    """
    Starting point !
    """

    ##############################################
    # Create the installer
    ##############################################
    installer = CPSInstaller(self, 'CPSForum')
    installer.log("Starting CPSForum Install")
    installer.verifyTool('portal_discussion', 'CPSForum', 'CPS Discussion Tool')

    #################################################
    # Forum-specific roles and permissions
    #################################################
    installer.log("Verifying CPSForum permissions")
    forum_perms = {
        ForumPost:
            ('Manager', 'Owner', 'Member', 'WorkspaceManager',
            'WorkspaceMember', 'WorkspaceReader', 'ForumPoster',
            'SectionManager', 'SectionReviewer', 'SectionReader',),
        ForumModerate:
            ('Manager', 'Owner', 'WorkspaceManager', 'ForumModerator',
            'SectionManager', 'SectionReviewer',),
    }

    # Forum Poster : Droit de poster un message
    # Forum Moderator : Droit de moderation du forum
    installer.verifyRoles(('ForumPoster','ForumModerator',))
    installer.setupPortalPermissions(forum_perms)

    ##########################################
    # SKINS
    ##########################################
    skins = {'cps_forum': 'Products/CPSForum/skins/forum_default',}
    installer.verifySkins(skins)
    installer.resetSkinCache()

    ##########################################
    # PORTAL TYPES
    ##########################################
    forum_types = installer.portal.getCPSForumTypes()
    installer.verifyFlexibleTypes(forum_types)

    installer.allowContentTypes('CPSForum', ('Workspace', 'Section'))
    ptypes = {
        'CPSForum' : {
            'allowed_content_types': (),
            'typeinfo_name': 'CPSForum: CPSForum',
            'add_meta_type': 'Factory-based Type Information',
        },
    }
    installer.verifyContentTypes(ptypes)

    # Portal Schemas
    forum_schemas = installer.portal.getCPSForumSchemas()
    installer.verifySchemas(forum_schemas)

    # Portal Layouts
    forum_layouts = installer.portal.getCPSForumLayouts()
    installer.verifyLayouts(forum_layouts)


    ########################################
    #   WORKFLOW ASSOCIATIONS
    ########################################
    ws_chains = { 'CPSForum': 'workspace_folder_wf',}
    se_chains = { 'CPSForum': 'section_folder_wf',}
    installer.verifyLocalWorkflowChains(installer.portal['workspaces'],
                                        ws_chains)
    installer.verifyLocalWorkflowChains(installer.portal['sections'],
                                        se_chains)


    ##########################################
    # WORKFLOW DEFINITION
    ##########################################
    # this is done to propagate forum permissions into portal_repository
    wfdef = {'wfid': 'forum_permissions_dummy_wf',
             'permissions': (ForumModerate,
                             ForumPost),
             }
    installer.verifyWorkflow(wfdef, {}, {}, {}, {})


    ##############################################
    # Actions
    ##############################################
    # This is just a straight move of functionality from the old installer,
    # But why are the two actions installed on different tools? /Lennart
    installer.deleteActions({'portal_actions': ['comment'],
                             'portal_discussion': ['comment'],})
    installer.verifyActions([
        {'tool':'portal_discussion',
         'id': 'comment',
         'name': 'action_comment',
         'action': 'string: ${object/absolute_url}/forum_post_form?'
                   'comment_mode=1',
         'condition': "python:object is not None and object.portal_type != "
                      "'CPSForum' and portal.portal_discussion."
                      "isCommentingAllowedFor(object)",
         'permission': 'View',
         'category': 'object',},
        {'tool': 'portal_actions',
         'id': 'status_history',
         'name': 'action_status_history',
         'action': 'string: ${object/absolute_url}/content_status_history',
         # XXX: this is as messy as what is done in cpsinstall
         'condition': "python:getattr(object, 'portal_type', None) not in "
                      "('Section', 'Workspace', 'Portal', 'Calendar', "
                      "'Event', 'CPSForum')",
         'permission': 'View',
         'category': 'workflow',}])

    ##############################################
    # i18n support
    ##############################################
    installer.setupTranslations()

    ##############################################
    # Finished!
    ##############################################
    installer.finalize()
    installer.log("End of CPSForum install")
    return installer.logResult()
