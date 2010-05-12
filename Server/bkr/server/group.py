from turbogears.database import session
from turbogears import controllers, expose, flash, widgets, validate, error_handler, validators, redirect, paginate, url
from turbogears.widgets import AutoCompleteField
from turbogears import identity, redirect
from cherrypy import request, response
from tg_expanding_form_widget.tg_expanding_form_widget import ExpandingForm
from kid import Element
from bkr.server.xmlrpccontroller import RPCRoot
from bkr.server.helpers import *
from bkr.server.widgets import myDataGrid, myPaginateDataGrid, AlphaNavBar

import cherrypy

# from bkr.server import json
# import logging
# log = logging.getLogger("bkr.server.controllers")
#import model
from model import *
import string

# Validation Schemas

class GroupFormSchema(validators.Schema):
    display_name = validators.UnicodeString(not_empty=True, max=256, strip=True)
    group_name = validators.UnicodeString(not_empty=True, max=256, strip=True)

class Groups(RPCRoot):
    # For XMLRPC methods in this class.
    exposed = False

    group_id     = widgets.HiddenField(name='group_id')
    display_name = widgets.TextField(name='display_name', label=_(u'Display Name'))
    group_name   = widgets.TextField(name='group_name', label=_(u'Group Name'))
    auto_users    = AutoCompleteField(name='user', 
                                     search_controller = url("/users/by_name"),
                                     search_param = "input",
                                     result_name = "matches")
    auto_systems  = AutoCompleteField(name='system', 
                                     search_controller = url("/by_fqdn"),
                                     search_param = "input",
                                     result_name = "matches")

    search_groups = AutoCompleteField(name='group', 
                                     search_controller = url("/groups/by_name?anywhere=1"),
                                     search_param = "name",
                                     result_name = "groups")

    group_form = widgets.TableForm(
        'Group',
        fields = [group_id, display_name, group_name],
        action = 'save_data',
        submit_text = _(u'Save'),
        validator = GroupFormSchema()
    )

    group_user_form = widgets.TableForm(
        'GroupUser',
        fields = [group_id, auto_users],
        action = 'save_data',
        submit_text = _(u'Add'),
    )

    group_system_form = widgets.TableForm(
        'GroupSystem',
        fields = [group_id, auto_systems],
        action = 'save_data',
        submit_text = _(u'Add'),
    )

    @expose(format='json')
    def by_name(self, name,*args,**kw):
        name = name.lower()
        if 'anywhere' in kw:
            search = Group.list_by_name(name, find_anywhere=True)
        else:
            search = Group.list_by_name(name)

        groups =  [match.group_name for match in search]
        return dict(groups=groups)
    
    @identity.require(identity.in_group("admin"))
    @expose(template='bkr.server.templates.form')
    def new(self, **kw):
        return dict(
            form = self.group_form,
            action = './save',
            options = {},
            value = kw,
        )

    
    def show_members(self,id): 
        user_member = ('User Members', lambda x: x.display_name)
        
        if identity.in_group('admin'):
            remove_link = (' ', lambda x: make_link('removeUser?group_id=%s&id=%s' % (id, x.user_id), 'Remove (-)'))
        
        user_fields = [user_member]
        if 'remove_link' in locals(): 
            user_fields.append(remove_link)

        return widgets.DataGrid(fields=user_fields)

    @expose(template='bkr.server.templates.grid')
    def systems(self,group_id=None,*args,**kw):
        if group_id is None:
            flash(_(u'Need a valid group to search on'))
            redirect(url('/groups'))
        systems = System.by_group(group_id)
        system_link = ('System', lambda x: x.link)
        group = Group.by_id(group_id)
        grid = myDataGrid(fields=[system_link])
        return dict(grid=grid,list=systems,title='Systems for group %s' % group.group_name,search_bar = None,object_count=systems.count())
    
    @expose(template='bkr.server.templates.group_users')
    def group_members(self,id, **kw):
        group = Group.by_id(id)
        usergrid = self.show_members(id)
        return dict(value = group,grid = usergrid)


    @identity.require(identity.in_group("admin"))
    @expose(template='bkr.server.templates.group_form')
    def edit(self, id, **kw):
        group = Group.by_id(id)
        usergrid = self.show_members(id) 
        systemgrid = widgets.DataGrid(fields=[
                                  ('System Members', lambda x: x.fqdn),
                                  (' ', lambda x: make_link('removeSystem?group_id=%s&id=%s' % (id, x.id), 'Remove (-)')),
                              ])
        return dict(
            form = self.group_form,
            system_form = self.group_system_form,
            user_form = self.group_user_form,
            action = './save',
            system_action = './save_system',
            user_action = './save_user',
            options = {},
            value = group,
            usergrid = usergrid,
            systemgrid = systemgrid,
            disabled_fields = ['System Members']
        )
    
    @identity.require(identity.in_group("admin"))
    @expose()
    @validate(form=group_form)
    @error_handler(edit)
    def save(self, **kw):
        if kw.get('group_id'):
            group = Group.by_id(kw['group_id'])
        else:
            group = Group()
            activity = Activity(identity.current.user, 'WEBUI', 'Added', 'Group', "", kw['display_name'] )
        group.display_name = kw['display_name']
        group.group_name = kw['group_name']
        flash( _(u"OK") )
        redirect(".")

    @identity.require(identity.in_group("admin"))
    @expose()
    @error_handler(edit)
    def save_system(self, **kw):
        system = System.by_fqdn(kw['system']['text'],identity.current.user)
        group = Group.by_id(kw['group_id'])
        group.systems.append(system)
        activity = GroupActivity(identity.current.user, 'WEBUI', 'Added', 'System', "", system.fqdn)
        sactivity = SystemActivity(identity.current.user, 'WEBUI', 'Added', 'Group', "", group.display_name)
        group.activity.append(activity)
        system.activity.append(sactivity)
        flash( _(u"OK") )
        redirect("./edit?id=%s" % kw['group_id'])

    @identity.require(identity.in_group("admin"))
    @expose()
    @error_handler(edit)
    def save_user(self, **kw):
        user = User.by_user_name(kw['user']['text'])
        group = Group.by_id(kw['group_id'])
        group.users.append(user)
        activity = GroupActivity(identity.current.user, 'WEBUI', 'Added', 'User', "", user.user_name)
        group.activity.append(activity)
        flash( _(u"OK") )
        redirect("./edit?id=%s" % kw['group_id'])

    @expose(template="bkr.server.templates.groups")
    @paginate('list', default_order='group_name', allow_limit_override=True)
    def index(self,*args,**kw):
        groups = session.query(Group)
        list_by_letters = []
        for elem in groups:
            first_letter = elem.group_name[0]
            list_by_letters.append(first_letter.capitalize()) 
        list_by_letters = set(list_by_letters) 

        if 'group' in kw:
            if 'text' in kw['group']:
                if 'starts_with' in kw['group']['text']:
                    groups = session.query(Group).filter(Group.group_name.like('%s%%' % kw['group']['text']['starts_with']))
                else:
                    groups = session.query(Group).filter_by(group_name = kw['group']['text'])

        if not 'admin' in identity.current.groups:
            group_name =('Group Name', lambda x: make_link('group_members?id=%s' % x.group_id,x.group_name))
            remove_link = None 
            template = "bkr.server.templates.grid"
        else:
            group_name =('Group Name', lambda x: make_edit_link(x.group_name,x.group_id))
            remove_link = (' ', lambda x: make_remove_link(x.group_id))  
        
       
        def f(x):
            if len(x.systems):
                return make_link('systems?group_id=%s' % x.group_id, 'System count: %s' % len(x.systems))
            else:
                return 'System count: 0' 

        systems = ('Systems', lambda x: f(x))
        display_name = ('Display Name', lambda x: x.display_name)
        
        potential_grid = (group_name,display_name,systems,remove_link)     
        actual_grid = [elem for elem in potential_grid if elem is not None]
   
        groups_grid = myPaginateDataGrid(fields=actual_grid)
        search_group_form = widgets.TableForm('SearchGroup',fields=[self.search_groups],action='.',submit_test=_(u'Search'),)
        return_dict = dict(title="Groups", 
                           grid = groups_grid,
                           alpha_nav_bar = AlphaNavBar(list_by_letters,'group'),
                           object_count = groups.count(),
                           search_bar = None,
                           search_groups = search_group_form, 
                           list = groups)
        if 'template' in locals():
            return_dict['tg_template'] = template

        return return_dict
  
    @identity.require(identity.in_group("admin"))
    @expose()
    def removeUser(self, group_id=None, id=None, **kw):
        group = Group.by_id(group_id)
        groupUsers = group.users
        for user in groupUsers:
            if user.user_id == int(id):
                group.users.remove(user)
                removed = user
                activity = GroupActivity(identity.current.user, 'WEBUI', 'Removed', 'User', removed.user_name, "")
                group.activity.append(activity)
        flash( _(u"%s Removed" % removed.display_name))
        raise redirect("./edit?id=%s" % group_id)

    @identity.require(identity.in_group("admin"))
    @expose()
    def removeSystem(self, group_id=None, id=None, **kw):
        group = Group.by_id(group_id)
        groupSystems = group.systems
        for system in groupSystems:
            if system.id == int(id):
                group.systems.remove(system)
                removed = system
                activity = GroupActivity(identity.current.user, 'WEBUI', 'Removed', 'System', removed.fqdn, "")
                sactivity = SystemActivity(identity.current.user, 'WEBUI', 'Removed', 'Group', group.display_name, "")
                group.activity.append(activity)
                system.activity.append(sactivity)
        flash( _(u"%s Removed" % removed.fqdn))
        raise redirect("./edit?id=%s" % group_id)

    @identity.require(identity.in_group("admin"))
    @expose()
    def remove(self, **kw):
        group = Group.by_id(kw['id'])
        session.delete(group)
        activity = Activity(identity.current.user, 'WEBUI', 'Removed', 'Group', group.display_name, "" )
        session.save_or_update(activity)
        flash( _(u"%s Deleted") % group.display_name )
        raise redirect(".")

    @expose(format='json')
    def get_group_users(self, group_id=None, *args, **kw):
        users = Group.by_id(group_id).users
        return [(user.user_id, user.display_name) for user in users]

    @expose(format='json')
    def get_group_systems(self, group_id=None, *args, **kw):
        systems = Group.by_id(group_id).systems
        return [(system.id, system.fqdn) for system in systems]

