from cefpython3 import cefpython as cef
import sys
import inspect
import loadHandler as lh

def fetcher(url):
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    windowInfo = cef.WindowInfo()
    # windowInfo.SetAsOffscreen(0)
    # windowInfo.SetTransparentPainting(True)
    browser = cef.CreateBrowserSync(windowInfo,
                          window_title=url)
    browser.SetClientHandler(lh.LoadHandler())
    # set_javascript_bindings(browser)

    browser.LoadUrl(url)

    cef.MessageLoop()
    cef.Shutdown()
    cef.QuitMessageLoop()

if __name__ == "__main__":
    fetcher("https://ipac.library.taichung.gov.tw/webpac/login_iframe.cfm")

