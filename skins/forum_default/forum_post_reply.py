##parameters=

parent_id = context.REQUEST.get('parent_id', None)
return context.forum_post_form(error_message='',
                               parent_id=parent_id)

