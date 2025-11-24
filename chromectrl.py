# -*- coding: utf-8 -*-
"""
Chrome browser control using Chrome DevTools Protocol.
Allows controlling a 2048 game running in Chrome via remote debugging.
"""

import json
import threading
import itertools

try:
    import websocket
except ImportError:
    websocket = None

# Python 3 compatibility
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    input = raw_input
except NameError:
    pass


class ChromeDebuggerControl(object):
    """
    Control Chrome using the debugging socket.
    
    Chrome must be launched using the --remote-debugging-port=<port> option for this to work!
    
    Example:
        chrome --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222
    """
    
    def __init__(self, port=9222):
        """
        Initialize Chrome debugger control.
        
        Args:
            port: Port number for Chrome remote debugging (default: 9222)
        """
        if websocket is None:
            raise NotImplementedError(
                "websocket-client library not available; cannot control Chrome.\n"
                "Please install it (pip install websocket-client) then try again."
            )
        
        # Obtain the list of pages
        pages = json.loads(urlopen('http://localhost:%d/json/list' % port).read())
        if len(pages) == 0:
            raise Exception("No pages to attach to!")
        elif len(pages) == 1:
            page = pages[0]
        else:
            print("Select a page to attach to:")
            for i, page in enumerate(pages):
                title = page['title']
                if len(title) > 100:
                    title = title[:100] + '...'
                print("%d) %s" % (i+1, title))
            while 1:
                try:
                    pageidx = int(input("Selection? "))
                    page = pages[pageidx-1]
                    break
                except Exception as e:
                    print("Invalid selection:", e)
        
        # Configure debugging websocket
        wsurl = page['webSocketDebuggerUrl']
        self.ws = websocket.create_connection(wsurl)
        
        self.requests = {}  # dictionary containing in-flight requests
        self.results = {}
        self.req_counter = itertools.count(1)
        
        self.thread = threading.Thread(target=self._receive_thread)
        self.thread.daemon = True
        self.thread.start()
        
        self._send_cmd_noresult('Runtime.enable')
    
    def _receive_thread(self):
        """Continually read events and command results."""
        while 1:
            try:
                message = json.loads(self.ws.recv())
                if 'id' in message:
                    id = message['id']
                    event = self.requests.pop(id, None)
                    if event is not None:
                        self.results[id] = message
                        event.set()
            except Exception as e:
                break
    
    def _send_cmd_noresult(self, method, **params):
        """Send a command and ignore the result."""
        id = next(self.req_counter)
        out = {'id': id, 'method': method}
        if params:
            out['params'] = params
        self.ws.send(json.dumps(out))
    
    def _send_cmd(self, method, **params):
        """Send a command and wait for the result to be available."""
        id = next(self.req_counter)
        out = {'id': id, 'method': method}
        if params:
            out['params'] = params
        
        # Receive thread will signal us when the response is available
        event = threading.Event()
        self.requests[id] = event
        self.ws.send(json.dumps(out))
        event.wait()
        
        resp = self.results.pop(id)
        if 'error' in resp:
            # Python 3 compatibility: use items() instead of iteritems()
            params_str = ', '.join('%s=%r' % (k, v) for k, v in params.items())
            raise Exception("Command %s(%s) failed: %s (%d)" % (
                method, params_str, resp['error']['message'], resp['error']['code']))
        return resp['result']
    
    def execute(self, cmd):
        """
        Execute JavaScript code in the browser.
        
        Args:
            cmd: JavaScript code to execute
        
        Returns:
            Result of the JavaScript evaluation
        """
        resp = self._send_cmd('Runtime.evaluate', expression=cmd)
        if 'exceptionDetails' in resp:
            raise Exception("JS evaluation threw an error: %s" % resp['result']['description'])
        result = resp['result']
        if 'value' in result:
            return result['value']
        if 'description' in result:
            return result['description']
        return None

