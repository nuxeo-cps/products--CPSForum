##parameters=forum_thread_ids=(),comment_mode=0,REQUEST=None

# $Id$

forum = context.getForumObject(comment_mode)
for id in forum_thread_ids:
    forum.delPost(id)

if REQUEST:
    if comment_mode:
        REQUEST.RESPONSE.redirect(
            context.absolute_url() + "/?comment_id=" + REQUEST.parent_id)
    else:
        REQUEST.RESPONSE.redirect(
            context.absolute_url() + "/?post_id=" + REQUEST.parent_id)
