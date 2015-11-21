# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from datetime import datetime
@auth.requires_login()
def index():
    delta = datetime.now()
    delta = delta.replace(year=delta.year-1)
    last = delta.replace(day=delta.day-1)
    next_day = delta.replace(day=delta.day+1)
    q2 = db.Journal_Events.created_on >= last
    q3 = db.Journal_Events.created_on <= next_day
    memories = db(q2 & q3).select()
    q1 = db.Journal_Events.created_by == session.auth.user.id
    rows = db(q1).select(orderby = db.Journal_Events.created_on)
    #shared = db(db.Tag.post==db.Journal_Events.id & db.tagged==session.auth.user.id).select()
    shares = []
    shared = db(db.Tag).select(join=db.Journal_Events.on(db.Tag.post==db.Journal_Events.id))
    for share in shared:
        if share.Tag.tagged == session.auth.user.id:
            shares.append(share)
    years = {}
    for row in rows:
        years[row.created_on.year] = '1'
    yrs = years.keys()
    yrs.sort(reverse=True)
    return locals()

@auth.requires_login()
def displayDetails():
    q1 = db.Journal_Events.created_by == session.auth.user.id
    rows = db(q1).select(orderby = db.Journal_Events.created_on)
    #rows = db(db.Journal_Events).select(q1)
    desc=[]
    i = 0
    for row in rows:
        string = row.Description[0:50]+"......."
        desc.append(string)
    return locals()

@auth.requires_login()
def createJournal():
    form = SQLFORM(db.Journal_Events).process()
    rows = db(db.Journal_Events).select()
    if form.accepted:
        session.last_id = form.vars.id
        redirect(URL('share_journals'))
    elif form.errors:
        response.flash = "Form Has Errors"
    else:
        response.flash = "Form First time displayed"
    return locals()


@auth.requires_login()
def share_journals():
    q1 = db.Journal_Events.id == session.last_id
    q2 = db.auth_user.id != session.auth.user.id
    rows = db(q1).select()
    users = db(q2).select()
    return locals()

@auth.requires_login()
def search():
    form = SQLFORM.grid(db.Journal_Events)
    return locals()

def monthSelect():
    session.year = request.args[0]
    q1 = db.Journal_Events.created_on >= datetime(int(session.year),1,1)
    rows = db(q1).select()
    months = {}
    for row in rows:
        months[row.created_on.month] = 'a'
    mnts = months.keys()
    mnts.sort()
    monthName = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    return locals()

@auth.requires_login()
def displayJournal():
    q1 = db.Journal_Events.created_on >= datetime(int(session.year),int(request.args[0]),1)
    mon = int(request.args[0])
    session.month = mon
    mon = mon + 1
    if mon > 12:
        mon = mon % 12
    q3 = db.Journal_Events.created_on <= datetime(int(session.year),mon,1)
    q2 = db.Journal_Events.created_by == session.auth.user.id
    rows = db(q1 & q2 & q3).select()
    #form = SQLFORM.grid(q1 & q2).select()
    #response.flash = q1
    c = 0
    for row in rows:
        c = 1
    return locals()

def getDetails():
    q1 = db.Journal_Events.id == request.args[0]
    row = db(q1).select()
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def addShare():
    shared_by = session.auth.user.id
    shared_to = int(request.vars.selector)
    post_id = session.last_id
    q1 = db.Tag.tagged == shared_to
    q2 = db.Tag.post == post_id
    rows = db(q1 & q2).select()
    if len(rows)==0:
        if db.Tag.insert(tagged_by=shared_by,tagged = shared_to,post = post_id):
            response.flash = "Shared"
        else:
            response.flash = "Unable to share try again"
    else:
        response.flash = "Already shared with that person"
    #return "Hello"
