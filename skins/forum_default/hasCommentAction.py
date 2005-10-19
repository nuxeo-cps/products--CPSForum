##parameters=
# $Id$
"""Determines whether current user will have 'comment' action in Actions box"""

from Products.CMFCore.utils import getToolByName

proxy_types = ('document', 'folderishdocument', 'btreefolderishdocument')
proxy_type = getattr(context.getTypeInfo(), 'cps_proxy_type', '')

res = False

if (proxy_type in proxy_types and
    getattr(context.getContent(), 'allow_discussion', None) == 1):
    forum = context.getForum4Comments().getContent()
    pmtool = getToolByName(context, 'portal_membership')
    is_anon = pmtool.isAnonymousUser()
    is_poster = pmtool.checkPermission('Forum Post', forum)
    res = context.isAllowedToPost(is_poster=is_poster,
                                  is_anon=is_anon,
                                  forum=forum)

return res
