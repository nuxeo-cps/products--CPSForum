##parameters=REQUEST

# $Id$

parent_id = REQUEST.get('parent_id', None)
return context.forum_post_form(error_message='',
                               parent_id=parent_id)

