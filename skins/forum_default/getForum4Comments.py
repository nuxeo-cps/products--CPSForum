##parameters=

# $Id$

"""Get current document's commenting forum ; create it if it does not exist

Lazy instantiation
"""

comment_tool = context.portal_discussion

return comment_tool.getForum4Comments(context)
