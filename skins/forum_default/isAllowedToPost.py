##parameters=is_poster=0,is_anon=1
# $Id$

"""Determine whether the current user has posting rights on a forum"""

forum = context.getContent()

if forum.anonymousPostsAllowed():
    return 1
else:
    if not is_anon and is_poster:
        return 1
    else:
        return 0
