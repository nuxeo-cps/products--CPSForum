##parameters=post_id=None,forum=None
# $Id$

"""Is the thread post_id belongs to locked or not?"""

if forum and post_id:
    return forum.belongsToLockedThread(post_id)

return 0
