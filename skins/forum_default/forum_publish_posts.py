##parameters=forum_thread_ids=(), REQUEST=None

# $Id$

forum = hasattr(context, 'getContent') and context.getContent() or context
for i in forum_thread_ids:
    forum.publishPost(i)

if REQUEST:
    REQUEST.RESPONSE.redirect(
        context.absolute_url() + "/?post_id=" + REQUEST.parent_id)

