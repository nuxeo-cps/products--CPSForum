##parameters=
#$Id$

forum_schema = {
    'moderation_mode': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:1',}},

    'allow_anon_posts': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:0',}},

    'send_moderation_notification': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:0',}},

    'frozen_forum': {
        'type': 'CPS Int Field',
        'data': {'is_searchabletext': 0,
                 'default_expr': 'python:0',}},

    }

return {'forum': forum_schema}
