from ctypes import windll, create_string_buffer, memmove

OpenClipboard = windll.user32.OpenClipboard
EmptyClipboard = windll.user32.EmptyClipboard
GetClipboardData = windll.user32.GetClipboardData
SetClipboardData = windll.user32.SetClipboardData
CloseClipboard = windll.user32.CloseClipboard
CF_UNICODETEXT = 13

GlobalAlloc = windll.kernel32.GlobalAlloc
GlobalLock = windll.kernel32.GlobalLock
GlobalUnlock = windll.kernel32.GlobalUnlock
GlobalSize = windll.kernel32.GlobalSize
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

unicode_type = type(u'')


def paste():
    text = None
    OpenClipboard(None)
    handle = GetClipboardData(CF_UNICODETEXT)
    pcontents = GlobalLock(handle)
    size = GlobalSize(handle)
    if pcontents and size:
        raw_data = create_string_buffer(size)
        memmove(raw_data, pcontents, size)
        text = raw_data.raw.decode('utf-16le').rstrip(u'\0')
    GlobalUnlock(handle)
    CloseClipboard()
    return text


def copy(s):
    if not isinstance(s, unicode_type):
        s = s.decode('mbcs')
    data = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(data) + 2)
    pcontents = GlobalLock(handle)
    memmove(pcontents, data, len(data))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()