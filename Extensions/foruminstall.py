import sys, os
from App.Extensions import getPath
from re import match
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.ExternalMethod.ExternalMethod import ExternalMethod


def foruminstall(self):
    
    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<html><head><title>CPSForum Install</title></head><body><pre>'+ \
                   '\n'.join(_log) + \
                   '</pre></body></html>'

        _log.append(bla)
        if (bla and zlog):
            LOG('ForumInstall:', INFO, bla)

    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("Starting CPSForum Install")

    portal = self.portal_url.getPortalObject()

    def portalhas(id, portal=portal):
        return id in portal.objectIds()
        
    # setup portal_type:
    pr("Verifying portal types")
    ttool = portal.portal_types
    ptypes = {
        'CPSForum' : ('CPSForum',
                    ),      
    }
    allowed_content_type = {
                            'Section' : ('Section',),
                            'Workspace' : ('Workspace', 'CPSForum'),
                            }
    
    ptypes_installed = ttool.objectIds()
    
    for prod in ptypes.keys():
        for ptype in ptypes[prod]:
            pr("  Type '%s'" % ptype)
            if ptype in ptypes_installed:
                ttool.manage_delObjects([ptype])
                pr("   Deleted")

            ttool.manage_addTypeInformation(
                id=ptype,
                add_meta_type='Factory-based Type Information',
                typeinfo_name=prod+': '+ptype
                )
            pr("   Installation")

           
    for ptype in allowed_content_type.keys():
        ttool[ptype].allowed_content_types = allowed_content_type[ptype]

    workspaces_id = 'workspaces'

    pr("Verifying local workflow association")
    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        pr("  Adding workflow configuration to %s" % workspaces_id)
        portal[workspaces_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()
    
    pr("  Add %s chain to portal type %s in %s of %s" %('workspace_content_wf','CPSForum','.cps_workflow_configuration', workspaces_id))
    wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
    wfc.manage_addChain(portal_type='CPSForum', chain='workspace_content_wf')

    # skins
    skins = ('forum_default',)
    paths = {'forum_default': 'Products/CPSForum/skins/forum_default'}
    
    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
            pr("  Creating skin")
    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        if skin_name != 'Basic':
            continue
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path and path[0] == 'custom':
            path = path[:1] + list(skins) + path[1:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
        pr(" Fixup of skin %s" % skin_name)


    pr("End of CPSForum install")
    return pr('flush')
