##parameters=forum_thread_ids=(),comment_mode=0,frm_start=None,REQUEST=None

# $Id$

forum = context.getContent()
forum.toggleThreadsLockStatus(forum_thread_ids, proxy=context)

if REQUEST is not None:
    if frm_start:
        url = "%s?post_id=%s&frm_start=%s" % (context.absolute_url(),
                                              REQUEST.parent_id, frm_start)
    else:
        url = "%s?post_id=%s" % (context.absolute_url(),
                                 REQUEST.parent_id)
    REQUEST.RESPONSE.redirect(url)
