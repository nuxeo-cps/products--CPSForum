##parameters=subject,author,message,parent_id=None,comment_mode=0,REQUEST=None

# $Id$

doc = context.getForumObject(comment_mode)

if (not doc) and comment_mode:
    #the forum holding comments might not exist if this is
    #the first post ; in this case create it
    doc = context.portal_discussion.addForum(context)

if (not author) or (author == ""):
    # XXX: this message must be translated
    msg = "Pseudo obligatoire"
    return context.forum_post_form(error_message=msg)

if (not parent_id) or parent_id.isspace():
    #FIXME: for doc comment forums, parent_id is sometimes '',
    #which is not equivalent to None as far as the thread
    #manager is concerned, so we put it back to None in those
    #cases ; but it would be better to find why it gets '' instead
    #of None when going through "New Thread"
    parent_id = None

new_id = doc.addForumPost(subject=subject, author=author,
                          message=message, parent_id=parent_id)

if REQUEST:
    if comment_mode:
        REQUEST.RESPONSE.redirect(
            context.absolute_url() + "/?comment_id=" + new_id)
    else:
        REQUEST.RESPONSE.redirect(
            context.absolute_url() + "/?post_id=" + new_id)

else:
    return new_id
