##parameters=subject,author,message,parent_id=None,frm_start=None,REQUEST=None

# $Id$

if not author:
    msg = 'error_author'
    return context.forum_post_form(error_message=msg, subject=subject,
                                   message=message)

if not subject:
    msg = 'error_subject'
    return context.forum_post_form(error_message=msg, author=author,
                                   message=message)

if not parent_id or parent_id.isspace():
    parent_id = None

post_id = context.computeId(compute_from=subject)

isAnon = context.portal_membership.isAnonymousUser()

if isAnon:
    context.portal_discussion.createAnonymousForumPost(context, post_id,
                                                  subject,
                                                  author,
                                                  message,
                                                  parent_id)
else:
    context.portal_workflow.invokeFactoryFor(context, 'ForumPost', post_id,
                                             subject=subject,
                                             author=author,
                                             message=message,
                                             parent_id=parent_id)
    forum = context.getContent()
    forum.newPostCreated(post_id, proxy=context)

if REQUEST is not None:
    if not isAnon:
        if frm_start:
            url = "%s?post_id=%s&frm_start=%s" % (context.absolute_url(),
                                              post_id, frm_start)
        else:
            url = "%s?post_id=%s" % (context.absolute_url(),
                                     post_id)
    else:
        if frm_start:
            url = "%s?frm_start=%s?portal_status_message=%s" % (context.absolute_url(),
                                                                frm_start,
                                                                'forum_psm_message_posted')
        else:
            url = "%s?portal_status_message=%s" % (context.absolute_url(),
                                                   'forum_psm_message_posted')
    REQUEST.RESPONSE.redirect(url)
else:
    return post_id
