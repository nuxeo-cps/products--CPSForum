##parameters=forum_thread_ids=(),comment_mode=0,REQUEST=None

# $Id$

forum = context.getContent()
forum.toggleThreadsLockStatus(forum_thread_ids, proxy=context)

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(
        context.absolute_url() + "/?post_id=" + REQUEST.parent_id)
