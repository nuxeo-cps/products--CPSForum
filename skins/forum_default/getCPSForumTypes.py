##parameters=
#$Id$
"""
the forum in CPSDocument
"""

forum_type = {
    'title': "portal_type_CPSForum_title",
    'description': "portal_type_CPSForum_description",
    'content_icon': 'forum_icon.gif',
    'product': 'CPSForum',
    'factory': 'addCPSForum',
    'filter_content_types': 1,
    'immediate_view': 'forum_view',
    'allow_discussion': 1,
    'filter_content_types': 1,
    'allowed_content_types': ('ForumPost',),
    'cps_is_searchable': 1,
    'cps_display_as_document_in_listing': 1,
    'cps_proxy_type': 'folder',
    'schemas': ['metadata', 'forum'],
    'layouts': ['common', 'forum'],
    'cps_workspace_wf': 'workspace_forum_wf',
    'cps_section_wf': 'section_forum_wf',
    'actions': ({'id': 'view',
                 'name': 'action_view',
                 'action': 'forum_view',
                 'permissions': ('View',),
                 },
                {'id': 'new_content',
                 'name': 'action_new_content',
                 'action': 'folder_factories',
                 'permissions': ('Forum Post',),
                 'visible': 0},
                {'id': 'contents',
                 'name': 'action_folder_contents',
                 'action': 'folder_contents',
                 'permissions': ('Forum Moderate',),
                 'visible' :0},
                {'id': 'edit',
                 'name': 'action_modify',
                 'action': 'cpsdocument_edit_form',
                 'permissions': ('Modify Folder Properties',),
                 },
                {'id': 'metadata',
                 'name': 'action_metadata',
                 'action': 'cpsdocument_metadata',
                 'permissions': ('View',)
                 },
                {'id': 'localroles',
                 'name': 'action_local_roles',
                 'action': 'forum_localrole_form',
                 'permissions': ('Change permissions',),
                 },
                ),
    }

forumpost_type = {
    'title': "portal_type_ForumPost_title",
    'description': "portal_type_ForumPost_description",
    'content_icon': 'discussionitem_icon.gif',
    'content_meta_type': 'CPS Document',
    'product': 'CPSDocument',
    'factory': 'addCPSDocument',
    'immediate_view': 'cpsdocument_edit_form',
    'allow_discussion': 0,
    'filter_content_types': 0,
    'cps_is_searchable': 1,
    'cps_display_as_document_in_listing': 1,
    'cps_proxy_type': 'document',
    'schemas': ['common', 'metadata', 'forumpost'],
    'layouts': ['forumpost'],
    'cps_workspace_wf': 'forum_post_wf',
    'cps_section_wf': 'forum_post_wf',
    }

return {'CPSForum': forum_type,
        'ForumPost': forumpost_type
        }
