##parameters=subject,author,message,parent_id=None,b_start=None,REQUEST=None

# $Id$

from ZTUtils import make_query

if not author:
    msg = 'error_author'
    return context.forum_post_form(error_message=msg)

if not subject:
    msg = 'error_subject'
    return context.forum_post_form(error_message=msg)

if not parent_id or parent_id.isspace():
    parent_id = None

post_id = context.computeId(compute_from=subject)
context.portal_workflow.invokeFactoryFor(context, 'ForumPost', post_id,
                                         subject=subject,
                                         author=author,
                                         message=message,
                                         parent_id=parent_id)

forum = context.getContent()
forum.newPostCreated(post_id, proxy=context)

if REQUEST is not None:
    if b_start:
        url = "%s?post_id=%s&b_start=%s" % (context.absolute_url(),
                                            post_id, b_start)
    else:
        url = "%s?post_id=%s" % (context.absolute_url(),
                                            post_id)
    REQUEST.RESPONSE.redirect(url)
else:
    return post_id
