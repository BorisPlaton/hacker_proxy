from configuration.settings import settings
from proxy.handler import ProxyHandler
from proxy.server import ProxyServer


def main():
    """Starts the forward proxy and handles incoming requests."""
    with ProxyServer((settings['PROXY_SERVER']['HOST'], settings['PROXY_SERVER']['PORT']), ProxyHandler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
