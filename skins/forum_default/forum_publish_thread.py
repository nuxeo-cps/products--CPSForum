##parameters=parent_id, REQUEST

# $Id$

doc = hasattr(context, 'getContent') and context.getContent() or context
doc.publishPost(parent_id)
REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+REQUEST.parent_id)


