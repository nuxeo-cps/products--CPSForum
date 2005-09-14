##parameters=post_author

# $Id$

"""Given the id/login of a forum poster, return his fullname."""
mtool = context.portal_membership
return mtool.getFullnameFromId(post_author)
