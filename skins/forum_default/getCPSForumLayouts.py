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
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'moderation_mode'}, ],
                 [{'widget_id': 'allow_anon_posts'}, ],
                 [{'widget_id': 'frozen_forum'}, ],
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
                'label_edit': 'cpsforum_label_subject',
                'label': 'cpsforum_label_subject',
                'display_width': 72,
                'size_max': 100,
            },
        },
        'Creator': {
            'type': 'String Widget',
            'data': {
                'fields': ['Creator'],
                'is_i18n': 1,
                'label_edit': 'label_creator',
                'label': 'label_creator',
                'readonly_layout_modes': ['create', 'edit'],
                'hidden_layout_modes': ['create'],
                'display_width': 40,
                'size_max': 50,
            },
        },
        'Description': {
            'type': 'Text Widget',
            'data': {
                'fields': ['Description'],
                'is_i18n': 1,
                'label_edit': 'cpsforum_label_message',
                'label': '',
                'css_class': 'ddescription',
                'width': 72,
                'height': 5,
                'render_format': 'text',
            },
        },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'Title'}, ],
                 [{'widget_id': 'Creator'}, ],
                 [{'widget_id': 'Description'}, ],
                 ],
        }
    }

return {'forum': forum_layout,
        'forumpost': forumpost_layout}
