##parameters=descendants=(), post_id='', frm_start=0, sort_by=None, display_mode='title', wf_display_mode='wf_icon', forum=None, REQUEST=None

# $Id$

#counter counts the message position in thread

import cgi

if forum is None:
    forum = context.getContent()

cpsmcat = context.Localizer.default
pending_i18n = cpsmcat('forum_pending_post')
unpublished_i18n = cpsmcat('forum_unpublished_post')
rejected_i18n = cpsmcat('forum_rejected_post')
published_i18n = cpsmcat('forum_published_post')

pmt = context.portal_membership
member = pmt.getAuthenticatedMember()
username = member.getId()
is_reviewer = context.portal_membership.checkPermission('Forum Moderate', context)
try:
    session_data = REQUEST.SESSION
except AttributeError:
    session_data = None

tree_display = getattr(forum, 'tree_display', 'title')

def getHeadline(post):
    subject = cgi.escape(post['subject'])
    if frm_start:
        headline = '<a href="%s?post_id=%s&frm_start=%s">%s</a>' % (context.absolute_url(),
                                                                    post['id'],
                                                                    frm_start,
                                                                    subject)
    else:
        headline = '<a href="%s?post_id=%s">%s</a>' % (context.absolute_url(),
                                                       post['id'],
                                                       subject)
    if post['id'] == post_id:
        # Rendering selected post (if any) with a bold font
        headline = '<strong>' + headline + '</strong>'
    if tree_display == '200fc':
        chunk = post['message']
        if len(chunk) > 200:
            chunk = chunk[:200] + ' ...'
        headline = '<div>' + headline + '</div><div>' + chunk + '</div>'
    elif tree_display == 'msg':
        headline = '<div>' + headline + '</div><div>' + post['message'] + '</div>'
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

    if frm_start:
        result = '<a href="./forum_branch_set?post_id=%s&action=%s&frm_start=%s">' % (post['id'], style, frm_start)
    else:
        result = '<a href="./forum_branch_set?post_id=%s&action=%s">' % (post['id'], style)
    result += '<img src="/p_/%s" align="middle" border="0" alt="%s" height="16" width="16" /></a>\n' % ( tree_icon, label)
    return result

def getStatusIcon(post):
    if wf_display_mode == 'wf_icon':
        r_state = post['review_state']
        if r_state == 'pending':
            return '<img src="%s" width="6" height="6" align="middle" alt="%s" title="%s" />' % (
                getattr(context, 'puce_attente.png').absolute_url(), pending_i18n, pending_i18n)
        elif r_state == 'unpublished':
            return '<img src="%s" width="6" height="6" align="middle" alt="%s" title="%s" />' % (
                getattr(context, 'puce_depub.png').absolute_url(), unpublished_i18n, unpublished_i18n)
        elif r_state == 'rejected':
            return '<img src="%s" width="6" height="6" align="middle" alt="%s" title="%s" />' % (
                getattr(context, 'puce_refuse.png').absolute_url(), rejected_i18n, rejected_i18n)
        else:
            return '<img src="/p_/sp" width="6" height="6" alt="" />'
    else:
        return '<img src="/p_/sp" width="6" height="6" alt="" />'

def getStatusLabel(post):
    r_state = post['review_state']
    if r_state == 'pending':
        return pending_i18n
    elif r_state == 'unpublished':
        return unpublished_i18n
    elif r_state == 'rejected':
        return rejected_i18n
    else:
        return published_i18n

def getLockIcon(post):
    if post['locked']:
        return context.getImgTag('lock.png',alt="locked")
    return '<img src="/p_/sp" width="6" height="6" alt="" />'

def getBranches(branches, id='ROOT', level=0, counter=0):
    if not len(branches):
        return ("",counter)

    result = ''
    
    for branch in branches:
        post = branch[0]
        if post['published'] or is_reviewer or username == post['author']:
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

            indent = 2 * min(level, 7)
            if is_reviewer:
                result += '<td><input type="checkbox" name="forum_thread_ids:list" value="%s" style="border:none" /></td>\n' % post['id']
                result += '<td>%s</td>\n' % getStatusIcon(post)
            else:
                result += '<td>&nbsp;</td>\n'
                result += '<td>%s</td>\n' % getStatusIcon(post)
            result += '<td>' + '&nbsp;' * indent
            if(more):
                result += getTreeIcon(post, style)
            else:
                result += '<img align="middle" src="/p_/sp" height="16" width="16" alt="" border="0" />'

            result += getHeadline(post)
            
            try:
                fullname = '<a href="javascript:void(0)" onclick="javascript:window.open(\'popupdirectory_entry_view?dirname=members&id=' + post['author'] + '\',\'wclose\',\'width=500,height=200,scrollbars=yes,toolbar=no,status=no,resizable=yes,left=20,top=30\')">' +\
                       cgi.escape(context.getPosterName(post['author'])) + '</a>'
            except KeyError:
                fullname = cgi.escape(context.getPosterName(post['author']))
            result += '</td>\n<td class="forumAuthorCell">%s</td>' % fullname
            ptime = post['creation'].strftime('%d/%m/%y %H:%M')
            if is_reviewer:
                #display thread lock status only for reviewers
                if wf_display_mode == 'wf_txt':
                    result += '\n<td class="forumDateCell">%s</td>\n<td class="forumWFCell %s">%s</td>' % (ptime, post['review_state'], getStatusLabel(post))
                else:
                    result += '\n<td class="forumDateCell">%s</td>' % ptime
                result += '\n<td>%s</td>' % getLockIcon(post)
            else:
                if wf_display_mode == 'wf_txt':
                    result += '\n<td class="forumDateCell">%s</td>\n<td colspan="2" class="forumWFCell %s">%s</td>' % (ptime, post['review_state'], getStatusLabel(post))
                else:
                    result += '\n<td colspan="2" class="forumDateCell">%s</td>' % ptime
            result += '</tr>\n\n'
            result += more

    return (result, counter)


def flatList(posts, sort_by):

    result = ''
    even = 1

    for post in posts:
        if post['published'] or is_reviewer or username == post['author']:
            if even:
                row_class = 'even'
            else:
                row_class = 'odd'
            even = not even
            result += '<tr id="thread_%s" class="%s">' % \
                      (post['id'], row_class)
            if is_reviewer:
                result += '<td><input type="checkbox" name="forum_thread_ids:list" value="%s" style="border:none"/></td>\n<td>%s</td>\n' % (post['id'], getStatusIcon(post))
            else:
                result += '<td>&nbsp;</td>\n<td>%s</td>\n' % getStatusIcon(post)
            result += '<td>' + getHeadline(post)
            
            fullname = '<a href="javascript:void(0)" onclick="javascript:window.open(\'popupdirectory_entry_view?dirname=members&id=' + post['author'] + '\',\'wclose\',\'width=500,height=200,scrollbars=yes,toolbar=no,status=no,resizable=yes,left=20,top=30\')">' + cgi.escape(context.getPosterName(post['author'])) + '</a>'
            result += '</td>\n<td class="forumAuthorCell">%s</td>' % fullname
            ptime = post['creation'].strftime('%d/%m/%y %H:%M')
            if is_reviewer:
                #display thread lock status only for reviewers
                if wf_display_mode == 'wf_txt':
                    result += '\n<td class="forumDateCell">%s</td>\n<td class="forumWFCell %s">%s</td>\n<td>%s</td></tr>\n\n' % (ptime, post['review_state'], getStatusLabel(post), getLockIcon(post))
                else:
                    result += '\n<td class="forumDateCell">%s</td>\n<td>%s</td></tr>\n\n' % (ptime, getLockIcon(post))
            else:
                if wf_display_mode == 'wf_txt':
                    result += '\n<td class="forumDateCell">%s</td>\n<td colspan="2" class="forumWFCell %s">%s</td></tr>\n\n' % (ptime, post['review_state'], getStatusLabel(post))
                else:
                    result += '\n<td colspan="2" class="forumDateCell">%s</td></tr>\n\n' % ptime

    return result

if display_mode != 'title' or (sort_by is not None and sort_by != 'threads'):
    result = flatList(descendants, sort_by)
else:
    (result, dummy) = getBranches(descendants)

return result

