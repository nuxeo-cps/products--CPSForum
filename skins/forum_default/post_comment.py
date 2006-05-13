##parameters=REQUEST=None

# $Id$

"""Comment a document"""

if context.portal_membership.checkPermission('Forum Post', context):

    forum = context.getForum4Comments()

    if REQUEST is not None and forum is not None:
        REQUEST.RESPONSE.redirect('%s/%s' %
                                  (forum.absolute_url(), 'forum_post_form'))
else:
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %
                                  (context.absolute_url(), 'psm_cpsforum_need_rights'))