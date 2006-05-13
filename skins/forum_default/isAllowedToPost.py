##parameters=is_poster=0,is_anon=1,forum=None
# $Id$

"""Determine whether the current user has posting rights on a forum"""
ret = 0
if forum and not forum.isFrozen():
    if ((is_anon and forum.anonymousPostsAllowed()) or
        (not is_anon and is_poster)):
        ret = 1

return ret
