##parameters=
# $Id$
"""Return custom layouts types."""

forum_layout = {
    'widgets': {
        'moderation_mode': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ['moderation_mode'],
                'is_i18n': 1,
                'label': 'forum_moderation',
                'label_edit': 'forum_moderation',
                'label_false': 'forum_a_posteriori',
                'label_true': 'forum_a_priori',
                'help': 'forum_help_moderation',
                },
            },
        'allow_anon_posts': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ['allow_anon_posts'],
                'is_i18n': 1,
                'label': 'forum_allow_anon_posts',
                'label_edit': 'forum_allow_anon_posts',
                },
            },
        'frozen_forum': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ['frozen_forum'],
                'is_i18n': 1,
                'label': 'forum_label_lock_forum',
                'label_edit': 'forum_label_lock_forum',
                },
            },
        'tree_display': {
            'type': 'Select Widget',
            'data': {
                'fields': ['tree_display'],
                'is_i18n': 1,
                'label': 'forum_label_tree_display',
                'label_edit': 'forum_label_tree_display',
                'vocabulary': 'forum_tree_voc',
                'translated': 1,
                },
            },
        'wf_display': {
            'type': 'Select Widget',
            'data': {
                'fields': ['wf_display'],
                'is_i18n': 1,
                'label': '',
                'label_edit': 'forum_label_wf_display',
                'vocabulary': 'forum_wf_display_voc',
                'translated': 1,
                },
            },
        'threads_per_page': {
            'type': 'Int Widget',
            'data': {
                'fields': ['threads_per_page'],
                'is_i18n': 1,
                'label': 'forum_label_threads_per_page',
                'label_edit': 'forum_label_threads_per_page',
                },
            },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'moderation_mode'}, ],
                 [{'widget_id': 'allow_anon_posts'}, ],
                 [{'widget_id': 'frozen_forum'}, ],
                 [{'widget_id': 'tree_display'}, ],
                 [{'widget_id': 'wf_display'}, ],
                 [{'widget_id': 'threads_per_page'}, ],
                 ],
        }
    }

forumpost_layout = {
    'widgets': {
        'Title': {
            'type': 'Heading Widget',
            'data': {
                'fields': ['Title'],
                'level': 1,
                'is_i18n': 1,
                'is_required': 1,
                'label_edit': 'forum_label_subject',
                'display_width': 72,
                'size_max': 200,
            },
        },
        'author': {
            'type': 'String Widget',
            'data': {
                'fields': ['author'],
                'is_i18n': 1,
                'label_edit': 'forum_label_postedby',
                'label': 'forum_label_postedby',
                'readonly_layout_modes': ['create', 'edit'],
                'hidden_layout_modes': ['create'],
                'display_width': 40,
                'size_max': 50,
            },
        },
        'Description': {
            'type': 'Rich Text Editor Widget',
            'data': {
                'fields': ['Description'],
                'is_i18n': 1,
                'label_edit': 'forum_label_message',
                'label': '',
                'css_class': 'ddescription',
                'width': 72,
                'height': 10,
                'render_format': 'text',
            },
        },
        'links': {
            'type': 'InternalLinks Widget',
            'data': {
                'fields': ['links'],
                'is_required': 0,
                'is_i18n': 1,
                'label_edit': 'forum_label_attachedFiles',
                'label': 'forum_label_attachedFiles',
                'hidden_empty': 1,
            },
        },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'Title'}, ],
                 [{'widget_id': 'author'}, ],
                 [{'widget_id': 'Description'}, ],
                 [{'widget_id': 'links'}, ],
                 ],
        }
    }

return {'forum': forum_layout,
        'forumpost': forumpost_layout}
