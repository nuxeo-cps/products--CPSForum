##parameters=subject,author,message,parent_id=None
new_id = context.cps_create_findid(id=subject)
doc = hasattr(context,'getContent') and context.getContent() or context

if (not author) or (author == ""):
    msg = "Pseudo obligatoire"
    return context.forum_post_form(error_message=msg)

new_id = doc.addForumPost(
        new_id,
        subject=subject,
        author=author,
        message=message,
        parent_id=parent_id,
    )

context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/?post_id="+new_id)

