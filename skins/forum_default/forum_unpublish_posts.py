##parameters=forum_thread_ids=(), REQUEST=None

# $Id$

for post_id in forum_thread_ids:
    post = getattr(context, post_id)
    review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')
    if review_state == 'published':
        review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')
        context.portal_workflow.doActionFor(post, 'unpublish')
        review_state = context.portal_workflow.getInfoFor(post, 'review_state', 'nostate')

if REQUEST:
    REQUEST.RESPONSE.redirect(
        context.absolute_url() + "/?post_id=" + REQUEST.parent_id)
