##parameters=mode=1,REQUEST=None

# $Id$

"""Activate/deactivate comments"""

if context.portal_membership.checkPermission('Forum manage comments', context):

    if mode == '1':
        context.portal_discussion.setAllowDiscussion(context, 1)
        psm = 'forum_psm_comments_activated'
    else:
        context.portal_discussion.setAllowDiscussion(context, 0)
        psm = 'forum_psm_comments_deactivated'

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %
                                  (context.absolute_url(), psm))

