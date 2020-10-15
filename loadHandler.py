import inspect
import debug as dbg

class LoadHandler(object):

    debug = True

    def __init__(self):
        self.debug = True

    def OnLoadStart(self, browser, frame):
        dbg.debugInfo(self.debug, browser.GetUrl())

    def OnLoadEnd(self, browser, frame, http_code):
        if http_code == 0:
            return

        url = browser.GetUrl()
        dbg.debugInfo(self.debug, http_code, url)

    def OnLoadingStateChange(self, browser, is_loading, can_go_back, can_go_forward):
        dbg.debugInfo(self.debug, is_loading, browser.GetUrl())

    def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url):
        dbg.debugInfo(self.debug, error_code, error_text_out, failed_url)


if __name__ == "__main__":
    LoadHandler()