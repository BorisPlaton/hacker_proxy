from socketserver import TCPServer


class ProxyServer(TCPServer):
    allow_reuse_address = True
