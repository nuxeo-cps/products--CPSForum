##parameters=subject,author,message,parent_id=None,comment_mode=0

new_id = context.computeId(compute_from=subject)
doc = context.getForumObject(comment_mode)

if (not doc) and comment_mode:
    #the forum holding comments might not exist if this is
    #the first post ; in this case create it
    doc = context.portal_comment.addForum(context)


if (not author) or (author == ""):
    msg = "Pseudo obligatoire"
    return context.forum_post_form(error_message=msg)

if (not parent_id) or parent_id.isspace():
    #FIXME: for doc comment forums, parent_id is sometimes '',
    #which is not equivalent to None as far as the thread
    #manager is concerned, so we put it back to None in those
    #cases ; but it would be better to find why it gets '' instead
    #of None when going through "New Thread"
    parent_id = None

new_id = doc.addForumPost(id=new_id, subject=subject, author=author,
                          message=message, parent_id=parent_id)

# FIXME: what if there is no REQUEST ?
if comment_mode:
    context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/?comment_id="+new_id)
else:
    context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+new_id)

