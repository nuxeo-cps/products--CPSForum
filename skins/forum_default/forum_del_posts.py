##parameters=forum_thread_ids=(),REQUEST=None

# $Id$

posts_to_delete = []

# prepare initial lists of posts to delete (from selection)
for post_id in forum_thread_ids:
    if post_id not in posts_to_delete:
        posts_to_delete.append(post_id)

# append descendant posts of selected posts to the list
# of posts to delete
forum = context.getContent()

def addDescendants(descendants, result):
    for descendant in descendants:
        did = descendant[0]['id']
        if did not in result:
            result.append(did)
        if descendant[1]:
            addDescendants(descendant[1],result)

for post_id in posts_to_delete:
    addDescendants(forum.getDescendants(post_id,proxy=context), posts_to_delete)

# actually delete posts
forum.delPosts(posts_to_delete, proxy=context)

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url())
