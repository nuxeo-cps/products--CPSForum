##parameters=mode=1,REQUEST=None

# $Id$

"""Activate/deactivate comments"""

if context.portal_membership.checkPermission('Forum manage comments', context):
    
    if mode == '1':
        kw = {'allow_discussion': 1,}
        context.getEditableContent().edit(**kw)
        psm = 'forum_psm_comments_activated'
    else:
        kw = {'allow_discussion': 0,}
        context.getEditableContent().edit(**kw)
        psm = 'forum_psm_comments_deactivated'

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %
                                  (context.absolute_url(), psm))

