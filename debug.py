import inspect

def debugInfo(isDebug, *argv):
    if isDebug:
        callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                    # 1 represents line at caller
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        print("[%s:%s:L%s] %s" % (info.filename, info.function, info.lineno, argv))