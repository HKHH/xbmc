#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import re
import json
from .network import MechanizeLogin, getTerritory
from .configs import *
from .common import Globals


def loadUsers():
    g = Globals()
    users = json.loads(getConfig('accounts.lst', '[]'))
    if not users:
        g.addon.setSetting('login_acc', '')
    return users


def loadUser(key='', empty=False, cachedUsers=None):
    g = Globals()
    def_keys = {'email': '', 'password': '', 'name': '', 'save': '', 'atvurl': '', 'baseurl': '', 'pv': False, 'mid': '', 'cookie': ''}
    cur_user = g.addon.getSetting('login_acc').decode('utf-8')
    users = cachedUsers if cachedUsers else loadUsers()
    user = None if empty else [i for i in users if cur_user == i['name']]
    if user:
        user = user[0]
        if key and key not in user.keys():
            user = getTerritory(user)
            if False is user[1]:
                g.dialog.notification(g.__plugin__, getString(30219), xbmcgui.NOTIFICATION_ERROR)
            user = user[0]
            addUser(user)
        return user.get(key, user)
    else:
        return def_keys.get(key, def_keys)


def addUser(user):
    g = Globals()
    addUser.user['save'] = g.addon.getSetting('save_login')
    users = loadUsers() if multiuser else []
    num = [n for n, i in enumerate(users) if user['name'] == i['name']]
    if num:
        users[num[0]] = user
    else:
        users.append(user)
    writeConfig('accounts.lst', json.dumps(users))
    if xbmc.getInfoLabel('Container.FolderPath') == g.pluginid:
        xbmc.executebuiltin('Container.Refresh')


def switchUser(sel=-1):
    g = Globals()
    users = loadUsers()
    sel = g.dialog.select(getString(30133), [i['name'] for i in users]) if sel < 0 else sel
    if sel > -1:
        if loadUser('name') == users[sel]['name']:
            return False
        user = users[sel]
        g.addon.setSetting('save_login', user['save'])
        g.addon.setSetting('login_acc', user['name'])
        xbmc.executebuiltin('Container.Refresh')
    return -1 < sel


def removeUser():
    g = Globals()
    cur_user = loadUser('name')
    users = loadUsers()
    sel = g.dialog.select(getString(30133), [i['name'] for i in users])
    if sel > -1:
        user = users[sel]
        users.remove(user)
        writeConfig('accounts.lst', json.dumps(users))
        if user['name'] == cur_user:
            g.addon.setSetting('login_acc', '')
            if not switchUser():
                xbmc.executebuiltin('Container.Refresh')


def renameUser():
    g = Globals()
    cur_user = loadUser('name')
    users = loadUsers()
    sel = g.dialog.select(getString(30133), [i['name'] for i in users])
    if sel > -1:
        keyboard = xbmc.Keyboard(users[sel]['name'], getString(30135))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            usr = keyboard.getText()
            if users[sel]['name'] == cur_user:
                g.addon.setSetting('login_acc', usr)
                xbmc.executebuiltin('Container.Refresh')
            users[sel]['name'] = usr
            writeConfig('accounts.lst', json.dumps(users))
