##parameters=
#$Id$
"""
Here are defined the vocabularies.
Please, follow the same pattern to add new ones.
"""

vocabularies = {
    'forum_tree_voc': {
        'type': 'CPS Vocabulary',
        'data': {'tuples': (
            ('title', 'Title', 'forum_label_display_title'),
            ('200fc', '200FirstChars', 'forum_label_display_200_fc'),
            ('msg', 'Message', 'forum_label_display_msg')),},
        },
    }

return vocabularies
