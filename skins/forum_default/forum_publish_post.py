##parameters=forum_thread_ids=(), REQUEST, **kw

#raise "DEBUG", str(forum_thread_ids)

# $Id$

doc = hasattr(context, 'getContent') and context.getContent() or context
for i in forum_thread_ids:
    doc.publishPost(i)

REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+REQUEST.parent_id)

