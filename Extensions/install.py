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
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CPSForum.CPSForumPermissions import ForumPost, ForumModerate,\
     ForumManageComments
from Products.CPSCore.CPSWorkflow import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE, \
     TRANSITION_BEHAVIOR_DELETE, TRANSITION_BEHAVIOR_MERGE, \
     TRANSITION_ALLOWSUB_CHECKOUT, TRANSITION_INITIAL_CHECKOUT, \
     TRANSITION_BEHAVIOR_CHECKOUT, TRANSITION_ALLOW_CHECKIN, \
     TRANSITION_BEHAVIOR_CHECKIN, TRANSITION_ALLOWSUB_DELETE, \
     TRANSITION_ALLOWSUB_MOVE, TRANSITION_ALLOWSUB_COPY
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION, \
     TRIGGER_AUTOMATIC

WebDavLockItem = 'WebDAV Lock items'
WebDavUnlockItem = 'WebDAV Unlock items'

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
        ForumManageComments:
            ('Manager', 'Owner', 'WorkspaceManager', 'SectionManager',
             'SectionReviewer')
    }

    # Forum Poster : Droit de poster un message
    # Forum Moderator : Droit de moderation du forum
    installer.verifyRoles(('ForumPoster', 'ForumModerator',))
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
            'allowed_content_types': ('ForumPost',),
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

    ##########################################
    # WORKFLOW DEFINITION
    ##########################################
    # this is done to propagate forum permissions into portal_repository
    wfdef = {'wfid': 'forum_permissions_dummy_wf',
             'permissions': (ForumModerate,
                             ForumPost),
             }
    installer.verifyWorkflow(wfdef, {}, {}, {}, {})
    
    # workflow for forums
    # in workspaces
    wfdef = {'wfid': 'workspace_forum_wf',
             'permissions': (View, ModifyPortalContent,
                             WebDavLockItem, WebDavUnlockItem,)
             }

    wfstates = {
        'work': {
            'title': 'Work',
            'transitions':('create_content', 'cut_copy_paste'),
            'permissions': {View: ('Manager', 'WorkspaceManager',
                                   'WorkspaceMember', 'WorkspaceReader',
                                   'ForumModerator', 'ForumPoster')},
            },
        }

    wftransitions = {
        'cut_copy_paste': {
            'title': 'Cut/Copy/Paste',
            'new_state_id': '',
            'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                    TRANSITION_ALLOWSUB_MOVE,
                                    TRANSITION_ALLOWSUB_COPY),
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'actbox_name': '',
            'actbox_category': '',
            'actbox_url': '',
            'props': {'guard_permissions':'',
                      'guard_roles':'Manager; WorkspaceManager; '
                                    'WorkspaceMember',
                      'guard_expr':''},
        },
        'create': {
            'title': 'Initial creation',
            'new_state_id': 'work',
            'transition_behavior': (TRANSITION_INITIAL_CREATE,),
            'clone_allowed_transitions': None,
            'actbox_category': 'workflow',
            'props': {'guard_permissions':'',
                      'guard_roles':'Manager; WorkspaceManager; '
                                    'WorkspaceMember',
                      'guard_expr':''},
        },
        'create_content': {
            'title': 'Create content',
            'new_state_id': 'work',
            'transition_behavior': (TRANSITION_ALLOWSUB_CREATE,
                                    TRANSITION_ALLOWSUB_CHECKOUT),
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'actbox_name': '',
            'props': {'guard_permissions':'Forum Post',
                      'guard_roles':'',
                      'guard_expr':''},
        },
    }
    installer.verifyWorkflow(wfdef, wfstates, wftransitions, {}, {})

    # in sections
    wfdef = {'wfid': 'section_forum_wf',
            'permissions': (View,)}

    wfstates = {
        'work': {
            'title': 'Work',
            'transitions': ('create_content', 'cut_copy_paste'),
            'permissions': {View: ('Manager', 'SectionManager',
                                   'SectionReviewer', 'SectionReader',
                                   'ForumModerator', 'ForumPoster'),
                            ModifyPortalContent: ('Manager', 'Owner',
                                                  'WorkspaceManager',
                                                  'WorkspaceMember',
                                                  'SectionManager',
                                                  'SectionReviewer',
                                                  'ForumModerator')},
        },
    }

    wftransitions = {
        'cut_copy_paste': {
            'title': 'Cut/Copy/Paste',
            'new_state_id': '',
            'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                    TRANSITION_ALLOWSUB_MOVE,
                                    TRANSITION_ALLOWSUB_COPY),
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'actbox_name': '',
            'actbox_category': '',
            'actbox_url': '',
            'props': {'guard_permissions': '',
                      'guard_roles': 'Manager; SectionManager; '
                                     'SectionReviewer; SectionReader',
                      'guard_expr': ''},
        },
        'create': {
            'title': 'Initial creation',
            'new_state_id': 'work',
            'transition_behavior': (TRANSITION_INITIAL_CREATE,),
            'clone_allowed_transitions': None,
            'actbox_category': 'workflow',
            'props': {'guard_permissions': '',
                      'guard_roles': 'Manager; SectionManager;',
                      'guard_expr': ''},
        },
        'create_content': {
            'title': 'Create content',
            'new_state_id': 'work',
            'transition_behavior': (TRANSITION_ALLOWSUB_CREATE,
                                    TRANSITION_ALLOWSUB_PUBLISHING),
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'Forum Post',
                      'guard_roles': '',
                      'guard_expr': ''},
        },
    }
    installer.verifyWorkflow(wfdef, wfstates, wftransitions, {}, {})
    
    # workflow for forum posts
    wfdef = {'wfid': 'forum_post_wf',
             'permissions': (View, ModifyPortalContent),
             'state_var': 'review_state'}

    wfstates = {
        'created': {
            'title': 'Created',
            'transitions': ('auto_publish', 'auto_moderate'), #'auto_publish', 
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'SectionManager', 'SectionReviewer'),
                            ModifyPortalContent: ('Manager', 'Owner',
                                                  'WorkspaceManager',
                                                  'SectionManager',
                                                  'SectionReviewer',
                                                  'ForumModerator')},
            },
        'pending': {
            'title': 'Awaiting acceptance',
            'transitions': ('publish',),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'SectionManager', 'SectionReviewer'),
                            ModifyPortalContent: ('Manager',
                                                  'WorkspaceManager',
                                                  'SectionManager',
                                                  'SectionReviewer',
                                                  'ForumModerator')},
            },
        'published': {
            'title': 'Public',
            'transitions': ('unpublish',),
            'permissions': {View: ('Manager', 'Owner', 'WorkspaceManager',
                                   'WorkspaceMember', 'WorkspaceReader',
                                   'SectionManager', 'SectionReviewer',
                                   'SectionReader', 'ForumPoster'),
                            ModifyPortalContent: ('Manager',)},
            }
        }

    wftransitions = {
        'create': {
            'title': 'Initial creation',
            'new_state_id': 'created',
            'transition_behavior': (TRANSITION_INITIAL_CREATE, ),
            'clone_allowed_transitions': None,
            'after_script_name': 'post_edit',
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'Forum Post',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        'auto_publish': {
            'title': 'No moderation, publishing',
            'new_state_id': 'published',
            'trigger_type': TRIGGER_AUTOMATIC,
            'clone_allowed_transitions': None,
            'props': {'guard_permissions': '',
                      'guard_roles':'',
                      'guard_expr':'python:container.getContent().moderation_mode == 0'},
            },
        'auto_moderate': {
            'title': 'Moderating',
            'new_state_id': 'pending',
            'trigger_type': TRIGGER_AUTOMATIC,
            'clone_allowed_transitions': None,
            'props': {'guard_permissions': '',
                      'guard_roles':'',
                      'guard_expr':'python:container.getContent().moderation_mode == 1'},
            },
        'publish': {
            'title': 'Publishing',
            'new_state_id': 'published',
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'Forum Moderate',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        'unpublish': {
            'title': 'Unpublishing',
            'new_state_id': 'pending',
            'clone_allowed_transitions': None,
            'trigger_type': TRIGGER_USER_ACTION,
            'props': {'guard_permissions': 'Forum Moderate',
                      'guard_roles':'',
                      'guard_expr':''},
            },
        }

    wfscripts = {
            'post_edit': {
                '_owner': None,
                'script': """\
##parameters=state_change
object = state_change.object
subject = state_change.kwargs.get('subject', '')
author = state_change.kwargs.get('author', '')
msg = state_change.kwargs.get('message', '')
pid = state_change.kwargs.get('parent_id', '')

kw = {'Title': subject,
      'Description': msg,
      'Creator': author,
      'parent_id': pid}

object.getEditableContent().edit(**kw)
"""
            },
        }

    wfvariables = {
        'subject': {
            'description': 'post subject',
            'default_expr': "python:state_change.kwargs.get('subject', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'author': {
            'description': 'post author',
            'default_expr': "python:state_change.kwargs.get('author', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'message': {
            'description': 'post text',
            'default_expr': "python:state_change.kwargs.get('message', '')",
            'for_status': 1,
            'update_always': 1,
            },
        'parent_id': {
            'description': 'post parent id',
            'default_expr': "python:state_change.kwargs.get('parent_id', '')",
            'for_status': 1,
            'update_always': 1,
            },
        }

    installer.verifyWorkflow(wfdef, wfstates, wftransitions,
                             wfscripts, wfvariables)

    ########################################
    #   WORKFLOW ASSOCIATIONS
    ########################################
    ws_chains = { 'CPSForum': 'workspace_forum_wf', 'ForumPost': 'forum_post_wf'}
    se_chains = { 'CPSForum': 'section_forum_wf', 'ForumPost': 'forum_post_wf'}
    installer.verifyLocalWorkflowChains(installer.portal['workspaces'],
                                        ws_chains)
    installer.verifyLocalWorkflowChains(installer.portal['sections'],
                                        se_chains)

    ##############################################
    # Actions
    ##############################################
    # This is just a straight move of functionality from the old installer,
    # But why are the two actions installed on different tools? /Lennart
    installer.deleteActions({'portal_actions': ['comment'],
                             'portal_discussion': ['comment'],})
    installer.verifyActions([
        {'tool':'portal_discussion',
         'id': 'activate_comments',
         'name': 'action_activate_comments',
         'action': 'string:${object/absolute_url}/set_comment_mode?mode=1',
         'condition': "python:getattr(object.getTypeInfo(),'cps_proxy_type','') == 'document' and object.getContent().allow_discussion == 0",
         'permission': 'Forum manage comments',
         'category': 'object',},
        {'tool':'portal_discussion',
         'id': 'deactivate_comments',
         'name': 'action_deactivate_comments',
         'action': 'string:${object/absolute_url}/set_comment_mode?mode=0',
         'condition': "python:getattr(object.getTypeInfo(),'cps_proxy_type','') == 'document' and object.getContent().allow_discussion == 1",
         'permission': 'Forum manage comments',
         'category': 'object',},
        {'tool':'portal_discussion',
         'id': 'comment',
         'name': 'action_comment',
         'action': "python:'/'+portal.portal_discussion.getCommentForumURL(object.absolute_url(relative=1))+'/forum_post_form'",
         'condition': "python:getattr(object.getTypeInfo(),'cps_proxy_type','') == 'document' and object.getContent().allow_discussion == 1",
         'permission': 'View',
         'category': 'object',},
        {'tool':'portal_discussion',
         'id': 'manage_comments',
         'name': 'action_manage_comments',
         'action': "python:'/'+portal.portal_discussion.getCommentForumURL(object.absolute_url(relative=1))+'/forum_view'",
         'condition': "python:getattr(object.getTypeInfo(),'cps_proxy_type','') == 'document' and object.getContent().allow_discussion == 1",
         'permission': 'Forum manage comments',
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
    # New listeners for events
    ##############################################
    installer.log("Checking doc deletion listener (for commenting forum mapping sync)")
    estool = installer.portal.portal_eventservice
    objs = estool.objectValues()
    subscribers = []
    for obj in objs:
        subscribers.append(obj.subscriber)
    if 'portal_discussion' in subscribers:
        installer.logOK()
    else:
        installer.log(" Creating portal_discussion subscriber")
        estool.manage_addSubscriber(subscriber='portal_discussion',
                                    action='document_deleted',
                                    meta_type='*',
                                    event_type='sys_del_object',
                                    notification_type='synchronous')
        
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
