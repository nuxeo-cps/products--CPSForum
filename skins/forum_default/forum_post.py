##parameters=subject,author,message,parent_id=None
new_id = context.computeId(compute_from=subject)
doc = hasattr(context, 'getContent') and context.getContent() or context

if (not author) or (author == ""):
    msg = "Pseudo obligatoire"
    return context.forum_post_form(error_message=msg)

new_id = doc.addForumPost(new_id, subject=subject, author=author,
                          message=message, parent_id=parent_id)

# FIXME: what if there is no REQUEST ?
context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+new_id)

