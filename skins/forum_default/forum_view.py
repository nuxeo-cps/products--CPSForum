## Script (Python) "forum_view"
##parameters=post_id=None, REQUEST=None
""" """

if(post_id is None):
    threads = context.getContent().getThreads()
    if(len(threads)>0):
        context.forum_view_main(post_id=threads[0]['id'])
    else:
        context.forum_view_main()
else:
    context.forum_view_main()
