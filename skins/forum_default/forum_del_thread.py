##parameters=parent_id,comment_mode

if comment_mode:
    doc = context.portal_comment.getDiscussionFor(context)
else:
    doc = hasattr(context, 'getContent') and context.getContent() or context
doc.delForumPost(parent_id)

context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/view")

