##parameters=post_id, forum

# $id:$

result = []
for i in forum.getThreads():
    result.append((i, forum.getDescendants(i['id']),))

return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=0, comment_mode=1,
                                       forum=forum)
