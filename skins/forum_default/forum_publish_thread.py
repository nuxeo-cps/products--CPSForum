##parameters=parent_id

doc = hasattr(context, 'getContent') and context.getContent() or context
doc.publishPost(parent_id)
context.REQUEST.RESPONSE.redirect(context.absolute_url()
    +"/?post_id="+context.REQUEST.parent_id)


