##parameters=descendants=(), visibility="inherit", post_id=''

# counter counts the message position in thread

from zLOG import LOG, DEBUG

pmt = context.portal_membership
is_reviewer = pmt.checkPermission('Review portal content',context)
username = pmt.getAuthenticatedMember().getId()
session_data = context.session_data_manager.getSessionData()

def getHeadline(post):
    headline = '<a href="%s/?post_id=%s">%s</a>' % (
            context.absolute_url(), post['id'], post['subject'])
    if(post['id']==post_id):
        headline = '<b>' + headline + '</b>'

    return headline

def getTreeIcon(post, style):
    if style == 'collapsed':
        tree_icon = 'pl'
        label = 'Expand'
        style = 'expanded'
    else:
        tree_icon = 'mi'
        label = 'Collapse'
        style = 'collapsed'

    result = '<a href="./forum_branch_set?post_id=%s;action=%s">' % \
            (post['id'], style)
    result += '<img src="/p_/%s" align="center" border=0 alt="%s" height="16" width="16"></a>\n' % \
            ( tree_icon, label)
    return result

def getStatusIcon(post):
    if not post['published']:
        #  TODO: Translate
        return '<img src="%s" width=6 height=6 align="mid" alt="Not published"/>' % (getattr(context, 'puce.gif').absolute_url())
    return '<img src="/p_/sp" width=6 height=6 alt=""/>'

def getBranches(branches, id='ROOT', level=0, counter=0):
    if not len(branches):
        return ("",counter)

    result = ''
    for branch in branches:
        post = branch[0]
        if post['published'] or is_reviewer or username == post['author']:
            counter += 1
            if counter%2:
                bgcolor = '#F0F0F0'
            else:
                bgcolor = '#FFFFFF'

            result += '<tr id="thread_%s" style="background-color:%s">' % \
                (post['id'], bgcolor)

            style = session_data.get('post_' + str(post['id']), None)
            if style <> 'collapsed':
                more,counter = getBranches(branch[1], post['id'], level+1, counter)
            else:
                more,counter = ' ',0

            indent = 5*(min(level,7))
            if is_reviewer:
                result += '<td><input type="checkbox" name="forum_thread_ids:list" value="%s" /></td>\n' % post['id']
                result += '<td>%s</td>\n' % getStatusIcon(post)
                result += ''
            else:
                result += '<td>&nbsp;</td><td>&nbsp;</td>'
            result += '<td><img src="/p_/sp" alt="" height=12 width=%s>\n' % str(indent+1)
            if(more):
                result += getTreeIcon(post, style)
            else:
                result += '<img align="center" src="/p_/sp" height="16" width="16" alt="" border="0">'

            result += getHeadline(post)

            dirtool = context.portal_metadirectories.members
            entry = dirtool.getEntry(post['author'])
            if entry is None:
                fullname = post['author']
            else:
                fullname = entry.get(dirtool.display_prop, post['author'])
            result += '</td>\n<td>%s</td>' % fullname
            ptime = post['modified'].strftime('%d/%m/%y %H:%M')
            result += '\n<td>%s</td>' % ptime
            result += '</tr>\n\n'
            result += more

    return (result, counter)

(result,dummy) = getBranches(descendants)

return result


