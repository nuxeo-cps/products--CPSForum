##parameters=descendants=(), post_id='', frm_start=0

# $Id$

#counter counts the message position in thread

import cgi
from zLOG import LOG, DEBUG

pmt = context.portal_membership
member = pmt.getAuthenticatedMember()
username = member.getId()
is_reviewer = context.portal_membership.checkPermission('Forum Moderate', context)
try:
    session_data = context.session_data_manager.getSessionData()
except AttributeError:
    session_data = None

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

    if frm_start:
        result = '<a href="./forum_branch_set?post_id=%s&action=%s&frm_start=%s">' % (post['id'], style, frm_start)
    else:
        result = '<a href="./forum_branch_set?post_id=%s&action=%s">' % (post['id'], style)
    result += '<img src="/p_/%s" align="middle" border="0" alt="%s" height="16" width="16" /></a>\n' % ( tree_icon, label)
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

def getMostRecentPost(max_date, posts):
    if posts:
        new_max_date = max_date
        for post in posts:
            if post[0]['modified'] > new_max_date:
                new_max_date = post[0]['modified']
            tmp_date = getMostRecentPost(new_max_date, post[1])
            if tmp_date > new_max_date:
                new_max_date = tmp_date
        return new_max_date
    else:
        return max_date

def threadSorter(x,y):
    x_most_recent_post = getMostRecentPost(x[0]['modified'], x[1])
    y_most_recent_post = getMostRecentPost(y[0]['modified'], y[1])
    if x_most_recent_post > y_most_recent_post:
        return -1
    elif x_most_recent_post < y_most_recent_post:
        return 1
    else:
        return 0

def getBranches(branches, id='ROOT', level=0, counter=0):

    # sort threads by most recent post (a thread whose most recent post is
    # more recent than another thread's most recent post gets displayed
    # before)
    branches.sort(threadSorter)
    return displayBranches(branches, id=id, level=level, counter=counter)

def displayBranches(branches, id='ROOT', level=0, counter=0):
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
                more, counter = displayBranches(branch[1], post['id'],
                                            level+1, counter)
            else:
                more, counter = ' ', 0

            indent = 5 * min(level, 7)
            if is_reviewer:
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
            
            fullname = cgi.escape(context.getPosterName(post['author']))
            result += '</td>\n<td class="forumAuthorCell">%s</td>' % fullname
            
            ptime = post['modified'].strftime('%d/%m/%y %H:%M')
            if is_reviewer:
                #display thread lock status only for reviewers
                result += '\n<td class="forumDateCell">%s</td>' % ptime
                result += '\n<td>%s</td>' % getLockIcon(post)
            else:
                result += '\n<td colspan="2" class="forumDateCell">%s</td>' % ptime
            result += '</tr>\n\n'
            result += more

    return (result, counter)

(result, dummy) = getBranches(descendants)

return result

