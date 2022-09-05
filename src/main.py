from configuration.settings import settings
from proxy.handlers import ProxyHandler
from proxy.server import ProxyServer


def main():
    """Starts the forward proxy and handles incoming requests."""
    proxy_server = ProxyServer(
        (
            settings['PROXY_SERVER']['HOST'],
            settings['PROXY_SERVER']['PORT']
        ),
        ProxyHandler,
    )
    with proxy_server as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
