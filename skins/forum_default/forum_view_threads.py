##parameters=post_id, threads=None, is_reviewer=None

doc = context.getContent();
result = []
for i in doc.getThreads():
    result.append((i, doc.getDescendants(i['id']),))

return context.forum_view_threads_main(post_id=post_id, descendants=result, 
                                       is_reviewer=is_reviewer)
