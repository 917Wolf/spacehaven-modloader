import os
import platform
import winreg
from steamfiles import acf
import ui.log

POSSIBLE_SPACEHAVEN_LOCATIONS = [
    # MacOS
    "/Applications/spacehaven.app",
    "/Applications/Games/spacehaven.app",
    "/Applications/Games/Space Haven/spacehaven.app",
    "./spacehaven.app",
    "../spacehaven.app",
    # could add default steam library location here for mac, unless mac installs steam games in the previous locations?

    # Windows
    "../spacehaven/spacehaven.exe",
    "../../spacehaven/spacehaven.exe",
    "../spacehaven.exe",
    "../../spacehaven.exe",
    "C:/Program Files (x86)/Steam/steamapps/common/SpaceHaven/spacehaven.exe",

    # Linux
    "../SpaceHaven/spacehaven",
    "../../SpaceHaven/spacehaven",
    "~/Games/SpaceHaven/spacehaven",
    ".local/share/Steam/steamapps/common/SpaceHaven/spacehaven",
]


    def autolocateSpacehaven(self):
        self.gamePath = None
        self.jarPath = None
        self.modPath = None
        
        # Open previous location if known
        try:
            with open("previous_spacehaven_path.txt", 'r') as f:
                location = f.read()
                if os.path.exists(location):
                    self.locateSpacehaven(location)
                    return
        except FileNotFoundError:
            ui.log.log("Unable to get last space haven location. Autolocating again.")
        
        # Steam based locator (Windows)
        try:
            registry_path = "SOFTWARE\\WOW6432Node\\Valve\\Steam" if (platform.architecture()[0] == "64bit") else "SOFTWARE\\Valve\\Steam"
            steam_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path), "InstallPath")[0]
            library_folders = acf.load(open(steam_path + "\\steamapps\\libraryfolders.vdf"), wrapper=OrderedDict)
            locations = [steam_path + "\\steamapps\\common\\SpaceHaven\\spacehaven.exe"]
            for key, value in library_folders["LibraryFolders"].items():
                if str.isnumeric(key): locations.append(value + "\\steamapps\\common\\SpaceHaven\\spacehaven.exe")
            for location in locations:
                if os.path.exists(location):
                    self.locateSpacehaven(location)
                    return
        except FileNotFoundError:
            ui.log.log("Unable to locate Steam registry keys, aborting Steam autolocator")

        for location in POSSIBLE_SPACEHAVEN_LOCATIONS:
            try: 
                location = os.path.abspath(location)
                if os.path.exists(location):
                    self.locateSpacehaven(location)
                    return
            except:
                pass
        ui.log.log("Unable to autolocate installation. User will need to pick manually.")


    def locateSpacehaven(self, path):
        if path is None:
            return

        if path.endswith('.app'):
            self.gamePath = path
            self.jarPath = path + '/Contents/Resources/spacehaven.jar'
            self.modPath = path + '/Contents/Resources/mods'

        elif path.endswith('.jar'):
            self.gamePath = path
            self.jarPath = path
            self.modPath = os.path.join(os.path.dirname(path), "mods")

        else:
            self.gamePath = path
            self.jarPath = os.path.join(os.path.dirname(path), "spacehaven.jar")
            self.modPath = os.path.join(os.path.dirname(path), "mods")

        if not os.path.exists(self.modPath):
            os.mkdir(self.modPath)

        ui.log.setGameModPath(self.modPath)
        ui.log.log("Discovered game at {}".format(path))
        ui.log.log("  gamePath: {}".format(self.gamePath))
        ui.log.log("  modPath: {}".format(self.modPath))
        ui.log.log("  jarPath: {}".format(self.jarPath))
        
        
        with open("previous_spacehaven_path.txt", 'w') as f:
            f.write(path)
        


        self.spacehavenText.delete(0, 'end')
        self.spacehavenText.insert(0, self.gamePath)
        
        self.modPath = [self.modPath, ]
        try:
            with open("extra_mods_path.txt", 'r') as f:
                for mod_path in f.read().split('\n'):
                    if mod_path.strip():
                        self.modPath.append(mod_path.strip())
        except:
            pass
        
