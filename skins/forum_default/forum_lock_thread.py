##parameters=forum_thread_ids=(),comment_mode=0,b_start=None,REQUEST=None

# $Id$

forum = context.getContent()
forum.toggleThreadsLockStatus(forum_thread_ids, proxy=context)

if REQUEST is not None:
    if b_start:
        url = "%s?post_id=%s&b_start=%s" % (context.absolute_url(),
                                            REQUEST.parent_id, b_start)
    else:
        url = "%s?post_id=%s" % (context.absolute_url(),
                                 REQUEST.parent_id)
    REQUEST.RESPONSE.redirect(url)
