from configuration.settings import settings
from proxy.handlers import ProxyHandler
from proxy.server import ProxyServer


def main():
    """Starts the forward proxy and handles incoming requests."""
    proxy_server = ProxyServer(
        (
            settings.proxy_settings['HOST'],
            settings.proxy_settings['PORT']
        ),
        ProxyHandler,
    )
    with proxy_server as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
