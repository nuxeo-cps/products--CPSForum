##parameters=parent_id,comment_mode

# $Id$

doc = context.getForumObject(comment_mode)

doc.delForumPost(parent_id)

context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/view")

