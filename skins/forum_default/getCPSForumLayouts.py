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
        'send_moderation_notification': {
            'type': 'Boolean Widget',
            'data': {
                'fields': ['send_moderation_notification'],
                'is_i18n': 1,
                'label': 'forum_send_moderation_notification',
                'label_edit': 'forum_send_moderation_notification',
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
                 [{'widget_id': 'send_moderation_notification'}, ],
                 [{'widget_id': 'frozen_forum'}, ],
                 ],
        }
    }

return {'forum': forum_layout}
