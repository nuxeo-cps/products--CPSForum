##parameters=parent_id,comment_mode,REQUEST

# $Id$

doc = context.getForumObject(comment_mode)

doc.delForumPost(parent_id)

REQUEST.RESPONSE.redirect(context.absolute_url() + "/view")

