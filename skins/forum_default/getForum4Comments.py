##parameters=

# $Id$

"""Get current document's commenting forum ; create it if it does not exist

Lazy instantiation
"""

comment_tool = context.portal_discussion

forum = None

# check whether the forum object exists or not
forum_url = comment_tool.getCommentForumURL(context.absolute_url(relative=1))
if forum_url:
    forum = context.restrictedTraverse(forum_url)

# if not create it
if not forum:
    no_content_wf_chain = {}
    #XXX: would be cleaner if based on .cps_worfklow_configuration's
    #     declared chains
    for ptype in context.portal_types.objectIds():
        no_content_wf_chain[ptype] = ''
    #create a wf and add chains to it 
    def wfSetup(folder, chains):
        if not '.cps_workflow_configuration' in folder.objectIds():
            folder.manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()
            wfc = getattr(folder, '.cps_workflow_configuration')
            for type, chain in chains.items():
                wfc.manage_addChain(portal_type=type, chain=chain)

    # check whether the forum object exists or not
    # if not create it (also create .discussions if necessary)
    parent_folder = context.aq_inner.aq_parent
    if '.cps_discussions' not in parent_folder.objectIds():
        context.portal_workflow.invokeFactoryFor(parent_folder, 'Workspace', '.cps_discussions')
    cpsmcat = context.Localizer.default
    discussion_folder = getattr(parent_folder, '.cps_discussions')
    kw = {'hidden_folder': 1,
          'Title': cpsmcat('forum_title_comments').encode('ISO-8859-15', 'ignore')}
    discussion_folder_c = discussion_folder.getEditableContent()
    discussion_folder_c.edit(**kw)
    comment_wf_chain = no_content_wf_chain.copy()
    comment_wf_chain.update({'CPSForum': 'workspace_forum_wf',
                             'ForumPost': 'forum_post_wf',
                            })
    wfSetup(discussion_folder, comment_wf_chain)
    context.portal_eventservice.notifyEvent('modify_object', discussion_folder, {})
    context.portal_eventservice.notifyEvent('modify_object', discussion_folder_c, {})
    existing_forum_ids = discussion_folder.objectIds()
    # forum's id is computed using the std script
    forum_id = context.computeId(compute_from=context.id,
                                 location=discussion_folder.this())
    context.portal_workflow.invokeFactoryFor(discussion_folder,
                                             'CPSForum', forum_id)
    forum = getattr(discussion_folder, forum_id)
    forum_c = forum.getEditableContent()
    kw = {'Title': cpsmcat('forum_title_comments_for').encode('ISO-8859-15', 'ignore')+' '+context.Title(),
          'Description': cpsmcat('forum_desc_comments').encode('ISO-8859-15', 'ignore')+' '+context.Title()}
    forum_c.edit(**kw)
    context.portal_eventservice.notifyEvent('modify_object', forum, {})

    # tell comment_tool that it is now activated and map it
    context.portal_discussion.registerCommentForum(proxy_path=context.absolute_url(relative=1),
                                                   forum_path=forum.absolute_url(relative=1))

return forum
