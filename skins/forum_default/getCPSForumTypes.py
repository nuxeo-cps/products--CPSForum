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
    'filter_content_types': 0,
    'cps_is_searchable': 1,
    'cps_display_as_document_in_listing': 1,
    'cps_proxy_type': 'folder',
    'schemas': ['metadata', 'common', 'forum'],
    'layouts': ['common', 'forum'],
    'actions': ({'id': 'view',
                 'name': 'action_view',
                 'action': 'forum_view',
                 'permissions': ('View',),
                 },
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

return {'CPSForum': forum_type,
        }
