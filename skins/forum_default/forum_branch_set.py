##parameters=post_id, action, REQUEST=None

# $Id$

from ZTUtils import make_query

session_data = context.session_data_manager.getSessionData()
session_data.set('post_' + str(post_id), action)

if REQUEST is not None:
    url = "%s?%s" % (context.absolute_url(), make_query(REQUEST.form))
    REQUEST.RESPONSE.redirect(url)
