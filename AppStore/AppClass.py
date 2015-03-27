#encoding=utf-8
from __future__ import unicode_literals

import time

class AppInfo:
    def __init__(self, trackid=-1, name=None, icon=None):
        self.trackid = trackid
        self.name = name
        self.scheme = None

    def __str__(self):
        log = "AppInfo:\n"
        log += "    %8s: %s\n"%("trackid", self.trackid)
        log += "    %8s: %s\n"%("name", self.name)
        log += "    %8s: %s\n"%("scheme", self.scheme)
        log += "    %8s: %s\n"%("icon60", self.icon60)
        log += "    %8s: %s\n"%("icon512", self.icon512)
        # log += "    %8s: %s\n"%("desc", self.desc)
        return log

    def toTuple(self):
        return (self.trackid, self.name, self.scheme, self.icon60, self.icon512, time.strftime("%Y_%m_%d_%H"))

    def toDict(self):
        result = {}
        result["id"] = self.trackid
        result["name"] = self.name
        result["icon60"] = self.icon60
        result["icon512"] = self.icon512
        
        return result

    def setAppInfo(self, appInfo):
        self.trackid = appInfo.get("trackId")
        self.icon60 = appInfo.get("artworkUrl60")
        self.icon512 = appInfo.get("artworkUrl512")
        self.desc = appInfo.get("description")
        self.name = appInfo.get("trackName")
