from cefpython3 import cefpython as cef
import sys
import loadHandler as lh

class tclib():

    url = ""
    browser = None
    cb = None
    borrow_books = []
    request_books = []
    available_books = []

    def __init__(self, accnt, pwd):
        assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"
        self.account = accnt
        self.password = pwd
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        cef.Initialize()
        windowInfo = cef.WindowInfo()
        # windowInfo.SetAsOffscreen(0)
        # windowInfo.SetTransparentPainting(True)
        self.browser = cef.CreateBrowserSync(windowInfo,
                            window_title=self.url)
        self.cb = callback(self)
        self.browser.SetClientHandler(self.cb)
        self.set_javascript_bindings()

    def set_javascript_bindings(self):
        # external = External(self.browser)
        bindings = cef.JavascriptBindings(
                bindToFrames=False, bindToPopups=False)

        bindings.SetFunction("pyCallbackBorrow", self.pyCallbackBorrow)
        bindings.SetFunction("pyCallbackRequest", self.pyCallbackRequest)
        bindings.SetFunction("pyCallbackRequestRemains", self.pyCallbackRequestRemains)
        bindings.SetFunction("pyCallbackRequestAvailable", self.pyCallbackRequestAvailable)
        # self.bindings.SetObject("external", external)
        self.browser.SetJavascriptBindings(bindings)

    def open_url(self, url):
        self.browser.LoadUrl(url)
        cef.MessageLoop()

    def login(self):
        print('login')
        self.open_url("https://ipac.library.taichung.gov.tw/webpac/login_iframe.cfm")

    def send_login_key(self, lib):
        lib.browser.ExecuteJavascript("$('#hidid').val('%s')" % lib.account)
        lib.browser.ExecuteJavascript("$('#password').val('%s')" % lib.password)
        lib.browser.ExecuteJavascript("$('#login_form').submit()")

    def get_borrow_books(self, lib):
        script = "var dict = {}; $('div.list_box').each(function(index) { var v = []; var k = $(this).find('div.title ul li:nth(2)').text().trim(); v[0] = $(this).find('div.content_d div.info p:contains(\"到期日\")').text().trim(); v[1] = $(this).find('div.content_d div.info p:contains(\"預約人數\")').text().trim(); dict[k]=v; })"
        lib.browser.ExecuteJavascript(script)
        lib.browser.ExecuteJavascript("pyCallbackBorrow('%s', dict)" % lib.account)

    def get_request_books(self, lib):
        script = "var dict = {}; $('div.list_box').each(function(index) { var k = $(this).find('a.bookname').text().trim(); var v = $(this).find('div.content_d div.info_long:contains(\"預約等候順位\")').text().trim().split('：')[1]; dict[k]=v; })"
        script_remains = "var n = $('div.list_box').find('div.content_d div.info_long:contains(\"移送至您的取書館中\")').length; var m = $('div.list_box').length - n;"
        lib.browser.ExecuteJavascript(script)
        lib.browser.ExecuteJavascript(script_remains)
        lib.browser.ExecuteJavascript("pyCallbackRequest('%s', dict)" % lib.account)
        lib.browser.ExecuteJavascript("pyCallbackRequestRemains('%s', m, n)" % lib.account)
        lib.browser.LoadUrl("https://ipac.library.taichung.gov.tw/webpac/shelf_requset_desirable.cfm")

    def get_available_books(self, lib):
        script = "var dict = {}; $('div.list_box').each(function(index) { var k = $(this).find('div.title ul li:nth(2)').text().trim(); var v = $(this).find('div.content_d div.info p:contains(\"保留日期\")').text().trim(); dict[k]=v; })"
        lib.browser.ExecuteJavascript(script)
        lib.browser.ExecuteJavascript("pyCallbackRequestAvailable('%s', dict)" % lib.account)

    def pyCallbackBorrow(self, account, cxt):
        if len(cxt) == 0:
            return

        for k,v in cxt.items():
            self.borrow_books.append(dict(ID=account.ljust(10), Book=k, result=v))

    def pyCallbackRequest(self, account, cxt):
        if len(cxt) == 0:
            return

        for k,v in cxt.items():
            self.request_books.append(dict(ID=account.ljust(10), Book=k, result=v))

    def pyCallbackRequestRemains(self, account, m, n):
        k = 0
        x = 4 - m
        for i in range(0, x):
            if (i+m+n) >= 6:
                break

            k+=1

        print("剩餘可借閱數量", k)

    def pyCallbackRequestAvailable(self, account, cxt):
        if len(cxt) == 0:
            return

        for k,v in cxt.items():
            self.available_books.append(dict(ID=account.ljust(10), Book=k, Due=v))

class callback(lh.LoadHandler):

    def __init__(self, lib):
        super().__init__()
        self.debug = True
        self.bLoadFinished = False
        self.lib = lib

    def OnLoadEnd(self, browser, frame, http_code):
        self.bLoadFinished = True
        super().OnLoadEnd(browser, frame, http_code)
        
        if browser.GetUrl().endswith("login_iframe.cfm"):
            tclib.send_login_key(self, self.lib)
            
        if browser.GetUrl().endswith("search.cfm"):
            browser.LoadUrl("https://ipac.library.taichung.gov.tw/webpac/shelf_borrow.cfm")

        if browser.GetUrl().endswith("shelf_borrow.cfm"):
            tclib.get_borrow_books(self, self.lib)
            browser.LoadUrl("https://ipac.library.taichung.gov.tw/webpac/shelf_request.cfm")

        if browser.GetUrl().endswith("shelf_request.cfm"):
            tclib.get_borrow_books(self, self.lib)
            browser.LoadUrl("https://ipac.library.taichung.gov.tw/webpac/shelf_requset_desirable.cfm")

        if browser.GetUrl().endswith("shelf_requset_desirable.cfm"):
            tclib.get_available_books(self, self.lib)
            print(self.lib.borrow_books, self.lib.request_books, self.lib.available_books)
            cef.QuitMessageLoop()
        # lib.browser.ExecuteJavascript("$('#loginBtn').click()") #Logout

if __name__ == "__main__":
    obj = tclib('test', 'test')
    obj.login()
    print(len(obj.borrow_books), len(obj.request_books), len(obj.available_books))

