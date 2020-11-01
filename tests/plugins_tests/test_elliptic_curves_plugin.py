from sslyze import ServerConnectivityTester, ServerNetworkLocationViaDirectConnection
from sslyze.plugins.elliptic_curves_plugin import (
    SupportedEllipticCurvesScanResult,
    SupportedEllipticCurvesImplementation,
)
from tests.markers import can_only_run_on_linux_64
from tests.openssl_server import ModernOpenSslServer


class TestEllipticCurvesPluginWithOnlineServer:
    def test_supported_curves(self):
        # Given a server to scan that supports ECDH cipher suites
        server_location = ServerNetworkLocationViaDirectConnection.with_ip_address_lookup("www.cloudflare.com", 443)
        server_info = ServerConnectivityTester().perform(server_location)

        # When scanning for supported elliptic curves, it succeeds
        result: SupportedEllipticCurvesScanResult = SupportedEllipticCurvesImplementation.scan_server(server_info)

        # And the result confirms that some curves are supported and some are not
        assert result.supports_ecdh_key_exchange
        assert result.supported_curves
        assert result.rejected_curves

        # And a CLI output can be generated
        assert SupportedEllipticCurvesImplementation.cli_connector_cls.result_to_console_output(result)


@can_only_run_on_linux_64
class TestEllipticCurvesPluginWithLocalServer:
    def test_supported_curves(self):
        # Given a server to scan that supports ECDH cipher suites with specific curves
        server_curves = ["X25519", "X448", "prime256v1", "secp384r1", "secp521r1"]
        with ModernOpenSslServer(groups=":".join(server_curves)) as server:
            server_location = ServerNetworkLocationViaDirectConnection(
                hostname=server.hostname, ip_address=server.ip_address, port=server.port
            )
            server_info = ServerConnectivityTester().perform(server_location)

            # When scanning the server for supported curves, it succeeds
            result: SupportedEllipticCurvesScanResult = SupportedEllipticCurvesImplementation.scan_server(server_info)

        # And the supported curves were detected
        assert set(server_curves) == {curve.name for curve in result.supported_curves}
