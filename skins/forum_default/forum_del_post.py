##parameters=forum_thread_ids=(),comment_mode=0

#doc = hasattr(context, 'getContent') and context.getContent() or context
doc = context.getForumObject(comment_mode)
for i in forum_thread_ids:
    doc.delForumPost(i)

if comment_mode:
    context.REQUEST.RESPONSE.redirect(context.absolute_url()
                                      + "/?comment_id=" + context.REQUEST.parent_id)

else:
    context.REQUEST.RESPONSE.redirect(context.absolute_url()
                                      + "/?post_id=" + context.REQUEST.parent_id)
