##parameters=comment_mode=0

# Returns the Forum object holding the comments associated with the current
# document if we are in comment mode, or the current Forum if we are in
# standard forum mode.

# $Id$

if comment_mode:
    return context.portal_discussion.getDiscussionForumFor(context)
else:
    return context.getContent()
