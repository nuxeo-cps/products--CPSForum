##parameters=post=None,forum=None,proxy=None
# $Id$

"""Is the thread post_id belongs to locked or not?"""

proxy = proxy or context

if forum and post:
    return forum.belongsToLockedThread(post, proxy=proxy)

return 0
