##parameters=
# $Id$
"""Determines whether current user will have 'comment' action in Actions box"""

proxy_types = ('document', 'folderishdocument', 'btreefolderishdocument')
proxy_type = getattr(context.getTypeInfo(), 'cps_proxy_type', '')

if proxy_type in proxy_types and context.getContent().allow_discussion == 1:
    forum = context.getForum4Comments().getContent()
    is_anon = context.portal_membership.isAnonymousUser()
    is_poster = context.portal_membership.checkPermission('Forum Post', forum)
    return context.isAllowedToPost(is_poster=is_poster,
                                   is_anon=is_anon,
                                   forum=forum)

return False
