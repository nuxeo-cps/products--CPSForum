##parameters=post_id, is_reviewer=None

# $Id$

forum = context.getContent()

try:
    session_data = context.session_data_manager.getSessionData()
    sort_by = session_data.get('frm_sort', None)
except AttributeError:
    sort_by = None

if forum.tree_display != 'title' or (sort_by is not None and sort_by != 'threads'):
    post_proxies = context.objectValues(['CPS Proxy Document'])
    result = [forum.getPostInfo(proxy) for proxy in post_proxies]

    if sort_by == 'subject':
        def subjectSorter(x,y):
            x_subject = x['subject']
            y_subject = y['subject']
            # do not take Re: into account when sorting
            if x_subject.lower().startswith('re: '):
                x_subject = x_subject[4:]
            if y_subject.lower().startswith('re: '):
                y_subject = y_subject[4:]
            if x_subject > y_subject:
                return 1
            elif x_subject < y_subject:
                return -1
            else:
                if x['creation'] > y['creation']:
                    return -1
                elif x['creation'] < y['creation']:
                    return 1
                else:
                    return 0
        result.sort(subjectSorter)
    elif sort_by == 'author':
        def authorSorter(x,y):
            x_author = x['author']
            y_author = y['author']
            if x_author > y_author:
                return 1
            elif x_author < y_author:
                return -1
            else:
                if x['creation'] > y['creation']:
                    return -1
                elif x['creation'] < y['creation']:
                    return 1
                else:
                    return 0
        result.sort(authorSorter)
    else:
        def dateSorter(x,y):
            if x['creation'] > y['creation']:
                return -1
            elif x['creation'] < y['creation']:
                return 1
            else:
                x_subject = x['subject']
                y_subject = y['subject']
                # do not take Re: into account when sorting
                if x_subject.lower().startswith('re: '):
                    x_subject = x_subject[4:]
                if y_subject.lower().startswith('re: '):
                    y_subject = y_subject[4:]
                if x_subject > y_subject:
                    return -1
                elif x_subject < y_subject:
                    return 1
                else:
                    return 0
        result.sort(dateSorter)
else:
    result = []
    for root_post in forum.getThreads(proxy=context):
        result.append((root_post, forum.getDescendants(root_post['id'],
                                                       proxy=context)))
    def getMostRecentPost(max_date, posts):
        if posts:
            new_max_date = max_date
            for post in posts:
                if post[0]['creation'] > new_max_date:
                    new_max_date = post[0]['creation']
                tmp_date = getMostRecentPost(new_max_date, post[1])
                if tmp_date > new_max_date:
                    new_max_date = tmp_date
            return new_max_date
        else:
            return max_date
    
    def threadSorter(x,y):
        x_most_recent_post = getMostRecentPost(x[0]['creation'], x[1])
        y_most_recent_post = getMostRecentPost(y[0]['creation'], y[1])
        if x_most_recent_post > y_most_recent_post:
            return -1
        elif x_most_recent_post < y_most_recent_post:
            return 1
        else:
            return 0
    result.sort(threadSorter)
    
return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=is_reviewer, forum=forum,
                                       sort_by=sort_by,
                                       display_mode=forum.tree_display)

