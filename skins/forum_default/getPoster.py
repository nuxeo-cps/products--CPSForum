##parameters=post_author

#given the id/login of a forum poster, return his fullname

dirtool = context.portal_metadirectories.members
entry = dirtool.getEntry(post_author)
if entry is None:
    return post_author
else:
    return entry.get(dirtool.display_prop, post_author)
