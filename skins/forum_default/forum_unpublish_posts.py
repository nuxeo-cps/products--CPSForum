##parameters=forum_thread_ids=(),frm_start=None,REQUEST=None

# $Id$

for post_id in forum_thread_ids:
    post = getattr(context, post_id)
    review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')
    if review_state == 'published':
        review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')
        context.portal_workflow.doActionFor(post, 'unpublish')
        review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')

if REQUEST:
    if frm_start:
        url = "%s?post_id=%s&frm_start=%s" % (context.absolute_url(),
                                              REQUEST.parent_id, frm_start)
    else:
        url = "%s?post_id=%s" % (context.absolute_url(),
                                 REQUEST.parent_id)
    REQUEST.RESPONSE.redirect(url)
