# Copyright (C) 2015 KillerInstinct
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lib.cuckoo.common.abstracts import Signature


class Multiple_UA(Signature):
    name = "multiple_useragents"
    description = "Network activity contains more than one unique useragent."
    severity = 3
    categories = ["network"]
    authors = ["KillerInstinct"]
    minimum = "1.2"
    evented = True
    ttps = ["T1071"]  # MITRE v6,7,8

    filter_apinames = set(["InternetOpenA", "InternetOpenW"])

    def __init__(self, *args, **kwargs):
        Signature.__init__(self, *args, **kwargs)
        self.useragents = list()
        self.procs = list()

    def on_call(self, call, process):
        # Dict whitelist with process name as key, and useragents as values
        whitelist = {
            "acrord32.exe": ["Mozilla/3.0 (compatible; Acrobat 5.0; Windows)"],
            "iexplore.exe": ["VCSoapClient", "Shockwave Flash"],
            "outlook.exe": ["OutlookSocialConnector/1.0", "Mozilla/5.0 (compatible; IE 11.0; Win32; Trident/7.0)"],
        }
        ua = self.get_argument(call, "Agent")
        proc = process["process_name"].lower()
        if proc in whitelist.keys() and ua in whitelist[proc]:
            return None

        else:
            if ua not in self.useragents:
                if self.results.get("target", {}).get("category", "") == "file" or proc != "iexplore.exe":
                    self.useragents.append(ua)
                    self.procs.append((process["process_name"], ua))
                    self.mark_call()

    def on_complete(self):
        if len(self.useragents) < 2:
            return False

        for item in self.procs:
            self.data.append({"process": item[0]})
            self.data.append({"user-agent": item[1]})

        return True
