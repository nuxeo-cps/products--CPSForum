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

import os, sys
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

from Products.CMFDefault.DiscussionTool import DiscussionTool
from Products.CPSForum.CommentTool import CommentTool

def cps_forum_i18n_update(self):
    """
    Importation of the po files for internationalization.
    For CPS itself and compulsory products.
    """
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cps_i18n_update:', INFO, bla)

    def primp(pr=pr):
        pr(" !!! Cannot migrate that component !!!")

    def prok(pr=pr):
        pr(" Already correctly installed")

    portal = self.portal_url.getPortalObject()
    def portalhas(id, portal=portal):
        return id in portal.objectIds()

    pr("Updating i18n support")

    Localizer = portal['Localizer']
    languages = Localizer.get_supported_languages()
    catalog_id = 'cpsforum'
    # Message Catalog
    if catalog_id in Localizer.objectIds():
        Localizer.manage_delObjects([catalog_id])
        pr(" Previous default MessageCatalog deleted for CPSForum")

    # Adding the new message Catalog
    Localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id=catalog_id,
        title='CPSForum messages',
        languages=languages,
        )

    defaultCatalog = Localizer.cpsforum

    # computing po files' system directory
    CPSForum_path = sys.modules['Products.CPSForum'].__path__[0]
    i18n_path = os.path.join(CPSForum_path, 'i18n')
    pr("   po files are searched in %s" % i18n_path)
    pr("   po files for %s are expected" % str(languages))

    # loading po files
    for lang in languages:
        po_filename = lang + '.po'
        pr("   importing %s file" % po_filename)
        po_path = os.path.join(i18n_path, po_filename)
        try:
            po_file = open(po_path)
        except (IOError, NameError):
            pr("    %s file not found" % po_path)
        else:
            defaultCatalog.manage_import(lang, po_file)
            pr("    %s file imported" % po_path)

    # Translation Service Tool
    if portalhas('translation_service'):
        translation_service = portal.translation_service
        pr (" Translation Sevice Tool found in here ")
        try:
            if getattr(portal['translation_service'], 'cpsforum', None) == None:
                # translation domains
                translation_service.manage_addDomainInfo('cpsforum','Localizer/'+'cpsforum')
                pr(" cpsforum domain set to Localizer/cpsforum")
        except:
            pass
    else:
        raise str('DependanceError'), 'translation_service'

    return pr('flush')

def install(self):
    """
    Statring point !
    """
    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<html><head><title>CPSForum Installer</title></head><body><pre>'+ \
                   '\n'.join(_log) + \
                   '</pre></body></html>'

        _log.append(bla)
        if bla and zlog:
            LOG('CPSForum Install:', INFO, bla)

    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("Starting CPSForum Install")

    portal = self.portal_url.getPortalObject()

    def portalhas(id, portal=portal):
        return id in portal.objectIds()

    #################################################
    # Forum-specific roles
    #################################################
    pr("Verifying forum roles")
    already = portal.valid_roles()
    for role in ('ForumPoster',     # Forum Poster : Droit de poster un message 
                 'ForumModerator',  # Forum Moderator : Droit de moderation du forum 
                 ):
        if role not in already:
            portal._addRole(role)
            pr(" Add role %s" % role)

    ##########################################
    # Comment Tool
    ##########################################
    pr("Installing CPS Discussion Tool")
    if portalhas('portal_discussion'):
        if isinstance(portal.portal_discussion,CommentTool):
            prok()
        else:
            pr(" Destroying existing CMF portal_discussion")
            portal.manage_delObjects(['portal_discussion',])
            pr(" Creating CPS Discussion Tool (portal_discussion)")
            portal.manage_addProduct["CPSForum"].manage_addTool('CPS Discussion Tool')
    else:
        pr(" Creating CPS Discussion Tool (portal_discussion)")
        portal.manage_addProduct["CPSForum"].manage_addTool('CPS Discussion Tool')

    #################################################
    # PORTAL TYPES
    #################################################

    pr("Verifying portal types")
    ttool = portal.portal_types
    ptypes = {
        'CPSForum' : ('CPSForum',
                                  ),
    }

    #################################################
    # AUTHORIZATING PORTAL TYPES (ws and sections)
    #################################################

    if 'Workspace' in ttool.objectIds():
        workspaceACT = list(ttool['Workspace'].allowed_content_types)
    else:
        workspaceACT = []

    if 'Section' in ttool.objectIds():
        sectionACT = list(ttool['Section'].allowed_content_types)
    else:
        sectionACT = []

    if 'CPSForum' not in  workspaceACT:
        workspaceACT.append('CPSForum')
    if 'CPSForum' not in  sectionACT:
        sectionACT.append('CPSForum')

    allowed_content_type = {
                            'Section' : sectionACT,
                            'Workspace' : workspaceACT,
                            }

    ptypes_installed = ttool.objectIds()

    for prod in ptypes.keys():
        for ptype in ptypes[prod]:
            pr("  Type '%s'" % ptype)
            if ptype in ptypes_installed:
                ttool.manage_delObjects([ptype])
                pr("   Deleted")

            ttool.manage_addTypeInformation(
                id=ptype,
                add_meta_type='Factory-based Type Information',
                typeinfo_name=prod+': '+ptype
                )
            pr("   Installation")


    for ptype in allowed_content_type.keys():
        ttool[ptype].allowed_content_types = allowed_content_type[ptype]
        
    ########################################
    #   WORKFLOW ASSOCIATIONS
    ########################################

    workspaces_id = 'workspaces'
    sections_id = 'sections'

    pr("Verifying local workflow association")

    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        pr("  Adding workflow configuration to %s" % workspaces_id)
        portal[workspaces_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()

    pr("  Add %s chain to portal type %s in %s of %s" %('workspace_folder_wf',
                                                        'CPSForum',
                                                        '.cps_workflow_configuration',
                                                        workspaces_id))
    wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
    wfc.manage_addChain(portal_type='CPSForum', chain='workspace_folder_wf')

    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        pr("  Adding workflow configuration to %s" % sections_id)
        portal[sections_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()

    pr("  Add %s chain to portal type %s in %s of %s" %('section_folder_wf',
                                                        'CPSForum',
                                                        '.cps_workflow_configuration',
                                                        sections_id))
    wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
    wfc.manage_addChain(portal_type='CPSForum', chain='section_folder_wf')

    ##########################################
    # SKINS
    ##########################################

    skins = ('cps_forum',)
    paths = {'cps_forum': 'Products/CPSForum/skins/forum_default',
             }

    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(\
                filepath=path, id=skin)
            pr("  Creating skin")
    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        if skin_name != 'Basic':
            continue
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path and path[0] == 'custom':
            path = path[:1] + list(skins) + path[1:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
        pr(" Fixup of skin %s" % skin_name)

    ##########################################
    # Permissions
    ##########################################
    pr("Verifying permissions")

    #use the same var for all 'Forum Post' strings as not doing so
    #causes an error in manage_permission (Forum Post invalid)
    forumpost = 'Forum Post'
    setDefaultRoles(forumpost,['ForumPoster', 'ForumModerator',])
    
    sections_perm = {
        forumpost:['ForumPoster', 'ForumModerator',],
        }
    workspaces_perm = {
        forumpost:['ForumPoster', 'ForumModerator',],
        }
    
    pr("Section")
    for perm, roles in sections_perm.items():
        portal[sections_id].manage_permission(perm, roles, 0)
        pr("  Permission %s" % perm)
    portal[sections_id].reindexObjectSecurity()
    pr("Workspace")
    for perm, roles in workspaces_perm.items():
        portal[workspaces_id].manage_permission(perm, roles, 0)
        pr("  Permission %s" % perm)
    portal[workspaces_id].reindexObjectSecurity()

    ##############################################
    # Actions
    ##############################################
    pr("Verifiying comment action for document")
    actions_to_keep = ()
    for action in portal['portal_actions'].listActions():
        if action.id == 'comment':
            pr(" Removing old comment action from portal_actions")
        else:
            actions_to_keep = actions_to_keep + (action,)
    portal['portal_actions']._actions = actions_to_keep
    actions_to_keep = ()
    for action in portal['portal_discussion'].listActions():
        if action.id == 'comment':
            pr(" Removing old comment action from portal_discussion")
        else:
            actions_to_keep = actions_to_keep + (action,)
    portal['portal_discussion']._actions = actions_to_keep
    pr(" Adding new comment action")
    portal['portal_discussion'].addAction(
        id='comment',
        name='action_comment',
        action='string: ${object/absolute_url}/forum_post_form?comment_mode=1',
        condition="python:object is not None and portal.portal_discussion.isCommentingAllowedFor(object)",
        permission='View',
        category='object')

    ##############################################
    # i18n support
    ##############################################

    pr(cps_forum_i18n_update(self))

    pr("End of CPSForum install")
    return pr('flush')
