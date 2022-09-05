from socketserver import TCPServer


class ProxyServer(TCPServer):
    """The proxy server responsible for accepting requests."""
    allow_reuse_address = True
