##parameters=REQUEST=None

# $Id$

"""Comment a document"""

if context.portal_membership.checkPermission('Forum manage comments', context):

    forum = context.getForum4Comments()

    if REQUEST is not None and forum is not None:
        REQUEST.RESPONSE.redirect('%s/%s' %
                                  (forum.absolute_url(), 'forum_view'))
