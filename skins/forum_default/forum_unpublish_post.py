##parameters=forum_thread_ids=(), REQUEST

# $Id$

doc = hasattr(context, 'getContent') and context.getContent() or context
for i in forum_thread_ids:
    doc.publishPost(i, 0)

REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+REQUEST.parent_id)


