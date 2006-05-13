##parameters=criterion, REQUEST=None

# $Id$

from ZTUtils import make_query

try:
    REQUEST.SESSION['frm_sort'] = criterion
except AttributeError:
    pass

if REQUEST is not None:
    url = "%s?%s" % (context.absolute_url(), make_query(REQUEST.form))
    REQUEST.RESPONSE.redirect(url)
