##parameters=criterion, REQUEST=None

# $Id$

from ZTUtils import make_query

session_data = context.session_data_manager.getSessionData()
session_data.set('frm_sort', criterion)

if REQUEST is not None:
    url = "%s?%s" % (context.absolute_url(), make_query(REQUEST.form))
    REQUEST.RESPONSE.redirect(url)
