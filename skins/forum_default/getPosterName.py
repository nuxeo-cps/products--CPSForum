##parameters=post_author

# $Id$

"""Given the id/login of a forum poster, return his fullname."""

dirtool = context.portal_directories.members
entry = dirtool.getEntry(post_author)
if entry is None:
    return post_author
else:
    return entry.get(dirtool.title_field, post_author)
