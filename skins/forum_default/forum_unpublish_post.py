##parameters=forum_thread_ids=()

doc = hasattr(context, 'getContent') and context.getContent() or context
for i in forum_thread_ids:
    doc.publishPost(i, 0)

context.REQUEST.RESPONSE.redirect(context.absolute_url()
    +"/?post_id="+context.REQUEST.parent_id)


