##parameters=
#$Id$

forum_schema = {
    'allow_discussion': {
        'type': 'CPS Int Field',
        'data': {
            'default_expr': 'python:1',
            'is_searchabletext': 0,
            },
        },
    'preview': {
        'type': 'CPS Image Field',
        'data': {
            'default_expr': 'nothing',
            'is_searchabletext': 0,
            },
        },
    'moderation_mode': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:1',}},
    'allow_anon_posts': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:0',}},
    'frozen_forum': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:0',}},
    'threads_per_page': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 }},
    }

forumpost_schema = {
    # subject and message are resp. stored in Title and Description
    'parent_id': {
        'type': 'CPS String Field',
        'data': {
            'is_searchabletext': 0,
            },
        },
    }

return {'forum': forum_schema,
        'forumpost': forumpost_schema}
