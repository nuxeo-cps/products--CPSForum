##parameters=descendants=(), post_id='', comment_mode=0

# $Id$

#counter counts the message position in thread
#forum will exist only when comment_mode is true

from zLOG import LOG,DEBUG

pmt = context.portal_membership
member = pmt.getAuthenticatedMember()
is_reviewer = member.has_permission('Forum Moderate', context)
username = member.getId()
try:
    session_data = context.session_data_manager.getSessionData()
except AttributeError:
    session_data = None

def getHeadline(post):
    if comment_mode:
        # If viewing forum as document inline comments,
        # the proper parameter name to give to cpsdocument_view
        # is comment_id
        param_name = 'comment_id'
        goto_comment = "#document_comment"
    else:
        # If viewing standard forum, the proper parameter name
        # to give to the forum is post_id
        param_name = 'post_id'
        goto_comment = ''
    headline = '<a href="%s/?%s=%s%s">%s</a>' % (
        context.absolute_url(), param_name, post['id'], goto_comment,
        post['subject'])
    if post['id'] == post_id:
        # Rendering select post (if any) with a bold font
        headline = '<strong>' + headline + '</strong>'
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

    result = '<a href="./forum_branch_set?post_id=%s;action=%s;mode=%s">' % \
            (post['id'], style, comment_mode)
    result += '<img src="/p_/%s" align="middle" border="0" alt="%s" height="16" width="16" /></a>\n' % \
            ( tree_icon, label)
    return result

def getStatusIcon(post):
    if not post['published']:
        #  TODO: Translate
        return '<img src="%s" width="6" height="6" align="middle" alt="Not published" />' % (
            getattr(context, 'puce.gif').absolute_url())
    return '<img src="/p_/sp" width="6" height="6" alt="" />'

def getLockIcon(post):
    if post['locked']:
        return context.getImgTag('lock.gif',alt="locked")
    return '<img src="/p_/sp" width="6" height="6" alt="" />'

def getBranches(branches, id='ROOT', level=0, counter=0):
    if not len(branches):
        return ("",counter)

    result = ''
    for branch in branches:
        post = branch[0]
        if comment_mode or post['published'] or is_reviewer or username == post['author']:
            counter += 1
            
            if counter%2:
                row_class = 'even'
            else:
                row_class = 'odd'
            
            result += '<tr id="thread_%s" class="%s">' % \
                      (post['id'], row_class)

            if session_data:
                style = session_data.get('post_' + str(post['id']), None)
            else:
                style = None
            if style <> 'collapsed':
                more, counter = getBranches(branch[1], post['id'],
                                            level+1, counter)
            else:
                more, counter = ' ', 0

            indent = 5 * min(level, 7)
            if comment_mode:
                #review buttons (checkbox and status) are shown
                #only in std forum mode, not in comments mode
                result += '<td><input type="checkbox" name="forum_thread_ids:list" value="%s" /></td>\n' % post['id']
                result += '<td><img src="/p_/sp" width="6" height="6" alt="" /></td>\n'
            elif is_reviewer:
                result += '<td><input type="checkbox" name="forum_thread_ids:list" value="%s" /></td>\n' % post['id']
                result += '<td>%s</td>\n' % getStatusIcon(post)
            else:
                result += '<td>&nbsp;</td>\n'
                result += '<td>%s</td>\n' % getStatusIcon(post)
            result += '<td><img src="/p_/sp" alt="" height="12" width="%s" />\n' % str(indent+1)
            if(more):
                result += getTreeIcon(post, style)
            else:
                result += '<img align="middle" src="/p_/sp" height="16" width="16" alt="" border="0" />'

            result += getHeadline(post)
            
            fullname = context.getPosterName(post['author'])
            result += '</td>\n<td class="forumAuthorCell">%s</td>' % fullname
            
            ptime = post['modified'].strftime('%d/%m/%y %H:%M')
            if is_reviewer:
                #display thread lock status only for reviewers
                result += '\n<td class="forumDateCell">%s</td>' % ptime
                result += '\n<td>%s</td>' % getLockIcon(post)
            else:
                result += '\n<td colspan="2">%s</td>' % ptime
            result += '</tr>\n\n'
            result += more

    return (result, counter)

(result, dummy) = getBranches(descendants)

return result

