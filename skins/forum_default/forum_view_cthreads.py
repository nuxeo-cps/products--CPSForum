##parameters=post_id, forum_proxy, forum

# $Id$

try:
    session_data = context.session_data_manager.getSessionData()
    sort_by = session_data.get('frm_sort', None)
except AttributeError:
    sort_by = None

if forum.tree_display != 'title' or (sort_by is not None and sort_by != 'threads'):
    post_proxies = forum_proxy.objectValues(['CPS Proxy Document'])
    post_infos = [forum.getPostInfo(proxy) for proxy in post_proxies]

    # 2147483647 = sys.maxint (we cannot import sys in this context)
    
    def subject_sortkey(item):
        subject = item['subject']
        date = "%011d" % (2147483647 - int(item['creation']))
        if subject.lower().startswith('re: '):
            return subject[4:] + date
        else:
            return subject + date

    def author_sortkey(item):
        date = "%011d" % (2147483647 - int(item['creation']))
        return item['author'] + date
        
    def date_sortkey(item):
        date = "%011d" % (2147483647 - int(item['creation']))
        subject = item['subject']
        if subject.lower().startswith('re: '):
            return date + subject[4:]
        else:
            return date + subject

    if sort_by == 'subject':
        make_sortkey = subject_sortkey
    elif sort_by == 'author':
        make_sortkey = author_sortkey
    else:
        make_sortkey = date_sortkey
        
    posts4sort = [(make_sortkey(post_info), post_info) for post_info in post_infos]
    posts4sort.sort()

    result = [x[1] for x in posts4sort]
        
else:
    threads = []
    for root_post in forum.getThreads(proxy=forum_proxy):
        threads.append((root_post, forum.getDescendants(root_post['id'],
                                                       proxy=forum_proxy)))

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

    def threadDate_sortkey(thread):
        most_recent_post_date = getMostRecentPost(thread[0]['creation'], thread[1])
        return "%011d" % (2147483647 - int(most_recent_post_date))

    threads4sort = [(threadDate_sortkey(thread), thread) for thread in threads]
    threads4sort.sort()

    result = [x[1] for x in threads4sort]

return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=0, forum=forum,
                                       sort_by=sort_by,
                                       display_mode=forum.tree_display)
