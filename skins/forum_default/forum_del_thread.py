##parameters=parent_id

doc = hasattr(context, 'getContent') and context.getContent() or context
doc.delForumPost(parent_id)

context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/view")

