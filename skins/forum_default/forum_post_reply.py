##parameters=error_message=''

parent_id=context.REQUEST.get('parent_id', None)
return context.forum_post_form(error_message=error_message, \
    parent_id=parent_id)

