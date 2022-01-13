import configparser
import os
import sys
import importlib

if 'posix' in sys.builtin_module_names:
    pass
if 'nt' in sys.builtin_module_names:
    import winreg

winreg_exists = importlib.find_loader('winreg')
if winreg_exists:
    import winreg
else:
    pass
    # do winreg stuff

class RegSettings:
    def __init__(self, main_section):
        self.main_section = main_section
        self.reg_entries = winreg.HKEY_CURRENT_USER

    def set_reg(self, name, value):
        try:
            winreg.CreateKey(self.reg_entries, self.main_section)
            with winreg.OpenKey(self.reg_entries, self.main_section, 0, winreg.KEY_WRITE) as registry_key:
                winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            # winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_reg(self, name, default=None):
        try:
            with winreg.OpenKey(self.reg_entries, self.main_section, 0, winreg.KEY_READ) as registry_key:
                value, regtype = winreg.QueryValueEx(registry_key, name)
            # winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return default

    def get_reg_int(self, name, default=None):
        try:
            with winreg.OpenKey(self.reg_entries, self.main_section, 0, winreg.KEY_READ) as registry_key:
                value_str, regtype = winreg.QueryValueEx(registry_key, name)
            # winreg.CloseKey(registry_key)
            value = int(value_str)
            return value
        except (WindowsError, ValueError):
            if default is None:
                return default
            else:
                return int(default)

    def del_reg(self, name):
        try:
            with winreg.OpenKey(self.reg_entries, self.main_section, 0, winreg.KEY_WRITE) as registry_key:
                winreg.DeleteValue(registry_key, name)
            # winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False


class IniSettings:
    def __init__(self, path, section):
        self.section = section
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def get_config(self):
        if not os.path.exists(self.path):

            config = configparser.ConfigParser()
            config.add_section(self.section)
            with open(self.path, "w") as config_file:
                config.write(config_file)
        config = configparser.ConfigParser()
        config.read(self.path)
        return config

    def get_ini(self, setting, default=None):
        try:
            if self.config.has_option(self.section, setting):
                value = self.config.get(self.section, setting)
            else:
                value = default
            return value
        except (OSError, ValueError):
            return default

    def get_ini_int(self, setting, default=None):
        try:
            if self.config.has_option(self.section, setting):
                value_str = self.config.get(self.section, setting)
            else:
                value_str = default
            value = int(value_str)
            return value
        except (OSError, ValueError) as exc:
            if default is None:
                return default
            else:
                return int(default)


    def set_ini(self, setting, value):
        try:
            self.config = configparser.ConfigParser()
            if not os.path.exists(self.path):
                if not os.path.exists(os.path.dirname(self.path)):
                    os.makedirs(os.path.dirname(self.path))
                self.config.add_section(self.section)
                with open(self.path, "w") as config_file:
                    self.config.write(config_file)
            self.config.read(self.path)
            self.config.set(self.section, setting, value)
            with open(self.path, "w") as config_file:
                self.config.write(config_file)
        except OSError as exc:
            print(f'OSError - failed to write parameter ({exc})')
            return False

    def del_ini(self, setting):
        if not os.path.exists(self.path):
            pass
        else:
            self.config.remove_option(self.section, setting)
            with open(self.path, "w") as config_file:
                self.config.write(config_file)
