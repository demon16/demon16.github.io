# -*- coding: utf-8 -*-
"""
version = 2018.06.02
"""

import ctypes
import inspect
import math
import os
import logging
import logging.handlers
import subprocess
import re
import requests
import time
import traceback

try:
    import win32api
    import win32gui
    import win32com
    import win32com.client
    import win32con
    import win32process
    import win32clipboard

    SHELL = win32com.client.Dispatch("WScript.Shell")
    from ctypes import wintypes
    from anytree import Node, RenderTree
except:
    traceback.print_exc()
import warnings

warnings.simplefilter("ignore")

system = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(system)


# def get_logger(file_level=logging.WARNING, stream_level=logging.INFO, filename=None, maxBytes=100000000, backupCount=100):
def get_logger(file_level=logging.WARNING, stream_level=logging.INFO, filename=None, interval=1, backupCount=7):
    filename = filename or inspect.getframeinfo(inspect.currentframe().f_back).filename
    system = os.path.splitext(os.path.basename(filename))[0]
    logdir = os.path.join(os.path.dirname(filename), "log")
    if not os.path.isdir(logdir):
        os.mkdir(logdir)
    logfile = os.path.join(logdir, "{}.log".format(system))
    logformat = logging.Formatter('[%(asctime)s] %(name)s %(lineno)d <%(levelname)s> %(message)s')

    log = logging.getLogger(system)
    log.setLevel(logging.DEBUG)

    # fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=maxBytes, backupCount=backupCount)
    fh = logging.handlers.TimedRotatingFileHandler(logfile, when='D', interval=interval, backupCount=backupCount,
                                                   encoding='utf-8')

    fh.setLevel(file_level)
    fh.setFormatter(logformat)
    log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(stream_level)
    sh.setFormatter(logformat)
    log.addHandler(sh)
    return log


def execute_command(command, cwd='.', shell=True, timeout=30, printing=True):
    def decode(s):
        try:
            return s.decode('gb18030')
        except:
            return s.decode('utf-8', errors='ignore')

    proc = subprocess.Popen(command, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    finally:
        stdout = decode(stdout)
        stderr = decode(stderr)
    if proc.returncode != 0:
        print(stderr) if printing else None
        return stderr
    else:
        print(stdout) if printing else None
        return stdout


def get_devices():
    """获取系统设备列表"""
    objSWbemServices = win32com.client.Dispatch('WbemScripting.SWbemLocator').ConnectServer('.', 'root\cimv2')
    # "SELECT * FROM Win32_PnPEntity WHERE deviceid like '%vid_1bd2&pid_0005%'"
    for item in objSWbemServices.ExecQuery('SELECT * FROM Win32_PnPEntity'):
        print('-' * 60)
        print(item.__dict__)
        print('-' * 60)
        for name in ('Availability', 'Caption', 'ClassGuid', 'ConfigManagerUserConfig',
                     'CreationClassName', 'Description', 'DeviceID', 'ErrorCleared', 'ErrorDescription',
                     'InstallDate', 'LastErrorCode', 'Manufacturer', 'Name', 'PNPDeviceID',
                     'PowerManagementCapabilities ',
                     'PowerManagementSupported', 'Service', 'Status', 'StatusInfo', 'SystemCreationClassName',
                     'SystemName'):
            a = getattr(item, name, None)
            if a is not None:
                print('%s: %s' % (name, a))


def create_admin_users(n=128, username_prefix='user_'):
    """在本机(Windows)创建n个管理员账户"""
    for i in range(1, n + 1):
        username = "{0}{1:03d}".format(username_prefix, i)
        for cmd in [
            'net user {} yb160101 /add /active:yes /expires:never /passwordchg:no /passwordreq:yes'.format(username),
            'net localgroup Users {} /del'.format(username),
            'net localgroup Administrators {} /add'.format(username)
        ]:
            execute_command(cmd)


def _query_login_users():
    """查询本机登录账户"""
    out = execute_command('query session')
    return re.findall(r'([^\s]+)\s+(\d+)\s+(\w+)', out)


def _is_user_logged_in(username):
    """判断指定账户是否已登录"""
    users = _query_login_users()
    return list(filter(lambda x: x[0] == username and x[2] == '运行中', users))


def _logout_user(username):
    """注销指定账户"""
    execute_command('logoff {}'.format(username))


def _logout_users():
    """注销所有账户"""
    return list(map(lambda x: _logout_user(x[0]), _query_login_users()))


def _login_users(n=64, username_prefix='user_', width=1024, height=768):
    """开启远程桌面登陆账户"""
    for i in range(1, n + 1):
        username = "{0}{1:03d}".format(username_prefix, i)
        _login_user(username, width, height)


def _login_user(username, width=1024, height=768):
    TargetPath = os.path.abspath("./runserver.cmd")
    ws = win32com.client.Dispatch("wscript.shell")
    shortcut = ws.CreateShortcut(
        "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\server.lnk".format(
            username))
    shortcut.TargetPath = TargetPath
    shortcut.WorkingDirectory = os.path.dirname(TargetPath)
    shortcut.IconLocation = TargetPath
    shortcut.Save()

    execute_command('cmdkey /delete:127.0.0.1')
    execute_command('cmdkey /generic:127.0.0.1 /user:{} /pass:P@ssw0rd'.format(username))
    execute_command('mstsc.exe /v:127.0.0.1 /w {0} /h {1}'.format(width, height))


def reset_users(n=64):
    """注销并重登录n个账户"""
    _logout_users()
    _login_users(n)


def is_user_admin():
    """判断当前进程是否为管理员身份运行"""
    return ctypes.windll.shell32.IsUserAnAdmin()


def kill_process(name=None, pid=None):
    """终止指定进程树"""
    username = os.environ.get("USERNAME")
    if pid:
        cmd = 'taskkill /F /PID {}'.format(pid)
    elif name:
        cmd = '''taskkill /F /FI "USERNAME eq {}" /IM {}'''.format(username, name)

    return execute_command(cmd)


def process_alive(pid):
    """判断指定进程是否存活"""
    for proc in win32com.client.GetObject('winmgmts:').InstancesOf('Win32_Process'):
        if proc.ProcessId == pid:
            return True


def mouse_single_click():
    """单击鼠标"""
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(win32gui.GetDoubleClickTime() / 1000 / 4)


def mouse_double_click():
    """双击鼠标"""
    mouse_single_click()
    mouse_single_click()


def GetWindowText(handle, encoding='utf16'):
    if encoding:
        buf_size = 2 * win32gui.SendMessage(handle, win32con.WM_GETTEXTLENGTH, 0, 0)
        if buf_size:
            buffer = win32gui.PyMakeBuffer(buf_size)
            win32gui.SendMessage(handle, win32con.WM_GETTEXT, buf_size, buffer)
            text = bytes(buffer[0: buf_size]).decode(encoding, errors="ignore")
            text = re.sub('''[^\w!@#$%^&().]''', "", text)
            return text
    return win32gui.GetWindowText(handle)


def SetForegroundWindow(handle, timeout=0.1, check=True):
    st = time.time()
    while time.time() - st < timeout:
        if win32gui.GetForegroundWindow() == handle:
            return True
        try:
            win32gui.SetForegroundWindow(handle)
            if not check:
                # win32gui.PostMessage(handle, win32con.WM_SETFOCUS, 0, 0)
                return True
        except:
            time.sleep(0.01)
    return False


def get_sub_handles(handle):
    handles = {}

    def _call(shandle, extra):
        extra[shandle] = handle

    if win32gui.FindWindowEx(handle, None, None, None):
        win32gui.EnumChildWindows(handle, _call, handles)
    return handles


def get_tree_handles(handle, recursive=True):
    """获取指定句柄下的句柄树"""
    handles = {handle: None}
    processed = set()

    while True:
        tasks = set(handles) - processed
        if not tasks:
            break
        for task in tasks:
            sub_handles = get_sub_handles(task)
            if sub_handles:
                handles.update(sub_handles)
        processed |= tasks
        if not recursive:
            break

    handles.pop(handle, None)
    return handles


def find_windows(**kwargs):
    title = kwargs.get('title', None)
    class_name = kwargs.get('class_name', None)
    process = kwargs.get('process', None)
    parent = kwargs.get('parent', 0)
    top_level_only = kwargs.get('top_level_only', False)
    visible = kwargs.get('visible', None)
    enabled = kwargs.get('enabled', None)
    width = kwargs.get('width', None)
    encoding = kwargs.get('encoding', None)
    if isinstance(width, (int, float)):
        min_width = max_width = int(width)
    elif isinstance(width, (tuple, list)) and len(width) == 2:
        min_width, max_width = width
        min_width = math.floor(min_width)
        max_width = math.ceil(max_width)
    height = kwargs.get('height', None)
    if isinstance(height, (int, float)):
        min_height = max_height = int(height)
    elif isinstance(height, (tuple, list)) and len(height) == 2:
        min_height, max_height = height
        min_height = math.floor(min_height)
        max_height = math.ceil(max_height)

    tree_handles = get_tree_handles(parent, recursive=not top_level_only)
    handles = []
    for handle in tree_handles:
        if isinstance(title, str):
            if encoding:
                if not GetWindowText(handle, encoding=encoding) == title:
                    continue
            else:
                if not win32gui.GetWindowText(handle) == title:
                    continue
        if process and not win32process.GetWindowThreadProcessId(handle)[-1] == process:
            continue
        if isinstance(class_name, str) and not win32gui.GetClassName(handle) == class_name:
            continue
        if visible is not None and not win32gui.IsWindowVisible(handle) == visible:
            continue
        if enabled is not None and not win32gui.IsWindowEnabled(handle) == enabled:
            continue
        if width or height:
            rect = win32gui.GetWindowRect(handle)
            if width and not min_width <= rect[2] - rect[0] <= max_width:
                continue
            if height and not min_height <= rect[3] - rect[1] <= max_height:
                continue
        handles.append(handle)
    return handles


def wait_find_windows(timeout=30, **kwargs):
    """在超时时间内返回特定查询条件的句柄列表"""
    st = time.time()
    while time.time() - st <= timeout:
        handles = find_windows(**kwargs)
        if handles:
            return handles
        time.sleep(0.01)
    else:
        return []


def type_char(handle, char, method):
    if method == 'shell':
        SHELL.SendKeys(char)
    elif method == 'post':
        win32gui.PostMessage(handle, win32con.WM_CHAR, ord(char), 0)
    elif method == 'send':
        win32api.SendMessage(handle, win32con.WM_SETTEXT, 0, char)
    time.sleep(0.001)


def get_system_dpi():
    """获取系统主屏幕的DPI值"""
    return ctypes.WinDLL("User32").GetDpiForSystem()


def get_system_dpi_ratio():
    """获取系统主屏幕的DPI比例"""
    return ctypes.WinDLL('User32').GetDpiForSystem() / 96


def kill_proc_tree(pid, include_parent=True, timeout=None, on_terminate=print):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    import os
    import psutil
    import signal

    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")

    Alive = []
    for sig in ['SIGTERM', 'SIGKILL']:
        if hasattr(signal, sig):
            sig = getattr(signal, sig)
            try:
                if Alive:
                    children = Alive
                else:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    if include_parent:
                        children.append(parent)
                for p in children:
                    p.send_signal(sig)
                gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
                Alive = alive
                if not Alive:
                    return True
            except:
                traceback.print_exc()
    return False


def clean_clipboard():
    """ 清空剪切板 """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.CloseClipboard()


def get_clipboard(timeout: float = 1.0):
    st = time.time()
    while time.time() < st + timeout:
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
            try:
                win32clipboard.OpenClipboard()
                cdata = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return cdata
            except:
                pass
        time.sleep(0.001)
    return ''


class MemoryObject:
    def __init__(self, parent, addr_start, length):
        self.parent = parent
        self.addr_start = addr_start
        self.length = length
        self.addr_end = addr_start + length
        self.update()
        self.changed = None

    def update(self):
        value = self.parent.get(self.addr_start, self.addr_end)
        if not hasattr(self, 'value'):
            self.value = value
            return True
        self.lastvalue = self.value
        self.value = value
        self.changed = self.lastvalue != self.value

    def getvalue(self, update=True):
        if update:
            self.update()
        return self.value

    def is_changed(self):
        self.update()
        return self.changed

    def re(self, pattern):
        if re.findall(pattern, self.getvalue(), re.IGNORECASE | re.DOTALL):
            return True


class MemoryScaner:
    def __init__(self, pid):
        self.pid = pid

        '''用特定模式扫描指定进程的指定内存段'''
        self.block_size = 65536
        OpenProcess = ctypes.windll.kernel32.OpenProcess
        OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        OpenProcess.restype = wintypes.HANDLE
        self.ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
        self.ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t,
                                           ctypes.POINTER(ctypes.c_size_t)]
        self.ReadProcessMemory.restype = wintypes.BOOL
        GetLastError = ctypes.windll.kernel32.GetLastError
        GetLastError.argtypes = None
        GetLastError.restype = wintypes.DWORD
        self.processHandle = OpenProcess(0x1F0FFF, False, self.pid)
        self.data = ctypes.create_string_buffer(self.block_size)
        self.bytesRead = ctypes.c_size_t()

    def init_scan(self, *args, **kwargs):
        self.results = self.scan(*args, **kwargs)
        self.results.sort(key=lambda x: x.addr_start)
        # self.print_results()

    def scan_changed(self):
        self.results = list(filter(lambda x: x.is_changed(), self.results))
        self.results.sort(key=lambda x: x.addr_start)
        # self.print_results()

    def scan_next(self, pattern):
        self.results = list(filter(lambda x: x.re(pattern), self.results))
        self.results.sort(key=lambda x: x.addr_start)
        # self.print_results()

    def print_results(self):
        print('-' * 50)
        for result in self.results:
            print(hex(result.addr_start), result.length, result.changed, result.getvalue())

    def get(self, addr_start, addr_end):
        output = b''
        for addr in range(addr_start, addr_end, self.block_size):
            length = min(self.block_size, addr_end - addr)
            self.ReadProcessMemory(self.processHandle, addr, ctypes.byref(self.data), length,
                                   ctypes.byref(self.bytesRead))
            output += self.data[:length]
        return output

    def scan(self, addr_start=0x00000000, addr_end=0xFFFFFFFF, pattern=b'\x00'):
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        results = []
        for addr in range(addr_start, addr_end, self.block_size):
            length = min(self.block_size, addr_end - addr)
            self.ReadProcessMemory(self.processHandle, addr, ctypes.byref(self.data), length,
                                   ctypes.byref(self.bytesRead))
            for m in pattern.finditer(self.data[:length]):
                mo = MemoryObject(parent=self, addr_start=addr + m.start(), length=m.end() - m.start())
                results.append(mo)
        return results

    def close(self):
        try:
            CloseHandle = ctypes.windll.kernel32.CloseHandle
            CloseHandle.argtypes = [wintypes.HANDLE]
            CloseHandle.restype = wintypes.BOOL
            CloseHandle(self.processHandle)
        except:
            pass


if __name__ == "__main__":
    st = time.time()
    for i in range(100):
        handles = find_windows(parent=0)
    ed = time.time()
    print(ed - st)
    print(len(handles))
