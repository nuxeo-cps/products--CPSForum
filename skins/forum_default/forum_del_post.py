##parameters=forum_thread_ids=(),comment_mode=0,REQUEST

# $Id$

doc = context.getForumObject(comment_mode)
for i in forum_thread_ids:
    doc.delForumPost(i)

if comment_mode:
    REQUEST.RESPONSE.redirect(context.absolute_url()
                                      + "/?comment_id=" + REQUEST.parent_id)

else:
    REQUEST.RESPONSE.redirect(context.absolute_url()
                                      + "/?post_id=" + REQUEST.parent_id)
