##parameters=comment_mode=0
#returns the Forum object holding the comments associated with the current
#document we are in comment mode, or the current Forum if we are in standard
#forum mode

# $id:$

if comment_mode:
    return context.portal_discussion.getDiscussionForumFor(context)
else:
    return context.getContent()
