import time
import socket
import paramiko
from contextlib import closing
from typing import Tuple, Optional, List, Dict

from utilities.utils import Utils
from ssh_tests.listen_inbound_ports_binary import PYTHON_BINARY


class SSHConnection:
    """
    SSHConnection class provides functionalities to establish SSH connections,
    install packages on the cloud server, and perform port checks.
    """

    # Constants
    CLOUD_0_INBOUND_CLOSE_PORT = 1000
    INBOUND_PORTS = [22, 443, 80, 1000]
    OUTBOUND_PORTS = [25, 587, 467]
    NETCAT_COMMAND = "sudo apt-get install -y netcat-traditional"
    PYTHON_COMMAND = "sudo python3 -c "
    LSBLK_COMMAND = "lsblk -o NAME,SIZE"
    EXTRA_STORAGE_NAME1 = "vdb"
    EXTRA_STORAGE_NAME2 = "vdc"
    NC_COMMAND = "nc -z smtp.mail.yahoo.com"
    UBUNTU = "Ubuntu"

    def __init__(self, private_key_file: str):
        """
        Initializes the SSHConnection with the path to the private SSH key file.

        Args:
            private_key_file (str): Path to the private SSH key file.
        """
        self.utils = Utils()
        self.private_key_file = private_key_file
        self.logger = self.utils.custom_logger()

    def install_package_on_cloud(self, package_command: str, ssh_connection: paramiko.SSHClient, delay: int = 3) -> bool:
        """
        Installs a package on the cloud server by executing the given command via SSH.

        Args:
            package_command (str): The command to install the package.
            ssh_connection (paramiko.SSHClient): The established SSH connection.
            delay (int, optional): Delay in seconds between retries. Defaults to 3.

        Returns:
            bool: True if installation is successful, False otherwise.
        """
        retry_count = 30
        self.logger.debug(f"Attempting to install package with command: {package_command}")
        for attempt in range(1, retry_count + 1):
            time.sleep(delay)
            try:
                stdin, stdout, stderr = ssh_connection.exec_command(package_command)
                return_code = stdout.channel.recv_exit_status()
                if return_code == 0:
                    self.logger.info(f"Installation successful for command: {package_command}")
                    return True
                else:
                    error_output = stderr.read().decode('utf-8').strip()
                    self.logger.error(f"Error installing package with command '{package_command}': {error_output}")
            except Exception as e:
                self.logger.error(f"Exception during package installation with command '{package_command}': {e}")
            self.logger.warning(f"Retrying package installation (Attempt {attempt}/{retry_count})...")
        self.logger.critical(f"Installation failed after {retry_count} attempts for command: {package_command}")
        return False

    def check_inbound_port(self, remote_ip: str, port: int) -> bool:
        """
        Checks if a specific inbound port on the remote IP is open.

        Args:
            remote_ip (str): The remote IP address to check.
            port (int): The port number to check.

        Returns:
            bool: True if the port is open, False otherwise.
        """
        self.logger.debug(f"Checking inbound port {port} on {remote_ip}")
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((remote_ip, port))
            if result == 0:
                self.logger.info(f"Port {port} is open on {remote_ip}")
                return True
            else:
                self.logger.fatal(f"Unable to connect to {remote_ip} on port {port}")
                return False

    def check_outbound_port(self, port: int, ssh_connection: paramiko.SSHClient) -> bool:
        """
        Checks if a specific outbound port is open by executing a netcat command via SSH.

        Args:
            port (int): The outbound port number to check.
            ssh_connection (paramiko.SSHClient): The established SSH connection.

        Returns:
            bool: True if the outbound port is open, False otherwise.
        """
        self.logger.debug(f"Checking outbound port {port} using netcat command.")
        try:
            # Modify the command to include the specific port
            telnet_command = f"{self.NC_COMMAND} {port}"
            stdin, stdout, stderr = ssh_connection.exec_command(telnet_command)
            return_code = stdout.channel.recv_exit_status()

            if return_code == 0:
                self.logger.info(f"Outbound port {port} is open on smtp.mail.yahoo.com")
                return True
            else:
                self.logger.info(f"Outbound port {port} is closed on smtp.mail.yahoo.com")
                return False
        except Exception as e:
            self.logger.error(f"Exception while checking outbound port {port}: {e}")
            return False

    def test_ssh_connection(
            self,
            ip_address: str,
            username: str,
            password: str,
            authenticate_with_key: bool,
            max_retries: int = 10,
            initial_delay: int = 3,  # Starting delay
            backoff_factor: float = 2.0,  # Multiplier for delay
            timeout: int = 200
    ) -> Tuple[bool, Optional[paramiko.SSHClient], Optional[str]]:
        """
        Attempts to establish an SSH connection to the given IP address using either a private key or password.
        Implements exponential backoff for retries.

        Args:
            ip_address (str): The IP address of the server to connect to.
            username (str): The SSH username.
            password (str): The SSH password.
            authenticate_with_key (bool): Whether to authenticate using a private key.
            max_retries (int, optional): Maximum number of connection attempts. Defaults to 10.
            initial_delay (int, optional): Initial delay in seconds between retries. Defaults to 1.
            backoff_factor (float, optional): Factor by which the delay increases. Defaults to 2.0.

        Returns:
            Tuple[bool, Optional[paramiko.SSHClient], Optional[str]]:
                - Connection success status.
                - The SSH client if connected, else None.
                - Error message if any, else None.
        """
        error: Optional[str] = None
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connection_params: Dict[str, object] = {
            "hostname": ip_address,
            "username": username,
            "timeout": timeout,
            "banner_timeout": timeout,
            "auth_timeout": timeout
        }

        if authenticate_with_key:
            try:
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                connection_params["pkey"] = private_key
                self.logger.debug("Configured SSH connection with private key.")
            except Exception as e:
                self.logger.error(f"Failed to load private key file: {e}")
                return False, None, f"Failed to load private key file: {e}"
        else:
            connection_params["password"] = password
            self.logger.debug("Configured SSH connection with password.")

        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.debug(f"Attempting SSH connection to {ip_address} (Attempt {attempt}/{max_retries})")
                ssh.connect(**connection_params)
                self.logger.info(
                    f"Successfully connected to {ip_address} using {'SSH KEY' if authenticate_with_key else 'password'}.")
                return True, ssh, None
            except paramiko.AuthenticationException:
                error = f"Authentication failed for user {username} on {ip_address} using {'SSH KEY' if authenticate_with_key else 'password'}."
                self.logger.fatal(error)
                break
            except paramiko.SSHException as e:
                error = f"SSH exception occurred while connecting to {ip_address}: {e}"
                self.logger.fatal(error)
            except (socket.error, Exception) as e:
                error = f"Connection error while connecting to {ip_address}: {e}"
                self.logger.error(error)
            if attempt < max_retries:
                self.logger.warning(f"Retrying SSH connection to {ip_address} after {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor  # Exponential backoff
        return False, None, error

    def port_rules(self, combined_data: Dict[int, Dict[str, object]], cloud_0: str, assert_data: List[str]) -> None:
        """
        Applies port rules based on the combined port data and updates assertion data accordingly.

        Args:
            combined_data (Dict[int, Dict[str, object]]): A dictionary containing port numbers and their statuses.
            cloud_0 (str): Identifier for CloudV 0.
            assert_data (List[str]): A list to append assertion failure messages.
        """
        self.logger.debug("Applying port rules based on combined port data.")
        for port, data in combined_data.items():
            port_open_status = data.get('Port Open', False)
            cloud_package = data.get('Cloud Package', '')

            if port in self.INBOUND_PORTS:
                if cloud_0 in cloud_package:
                    if port == self.CLOUD_0_INBOUND_CLOSE_PORT:
                        if port_open_status:
                            self.logger.fatal(f"Inbound port {port} is open for {cloud_package}")
                            assert_data.append(f"{cloud_package} port {port} is open.")
                        else:
                            self.logger.info(f"Inbound port {port} is closed for {cloud_package}")
                    else:
                        if port_open_status:
                            self.logger.info(f"Inbound port {port} is open for {cloud_package}")
                        else:
                            self.logger.info(f"Inbound port {port} is closed for {cloud_package}")
                            assert_data.append(f"{cloud_package} port {port} is closed.")
                else:
                    if port_open_status:
                        self.logger.info(f"Inbound port {port} is open for {cloud_package}")
                    else:
                        self.logger.fatal(f"Inbound port {port} is closed for {cloud_package}")
                        assert_data.append(f"{cloud_package} port {port} is closed.")
            elif port in self.OUTBOUND_PORTS:
                if port_open_status:
                    self.logger.fatal(f"Outbound port {port} is open for {cloud_package}")
                    assert_data.append(f"{cloud_package} port {port} is open.")
                else:
                    self.logger.info(f"Outbound port {port} is closed for {cloud_package}")

    def check_ports(
        self,
        ssh: paramiko.SSHClient,
        cloud_server_ip: str,
        connection_successful: bool,
        cloud_package: str,
        ssh_test_interface: str,
        operating_system: str,
        cloud_0: str,
        assert_data: List[str]
    ) -> None:
        """
        Checks the status of inbound and outbound ports on the cloud server.

        Args:
            ssh (paramiko.SSHClient): The established SSH connection.
            cloud_server_ip (str): The IP address of the cloud server.
            connection_successful (bool): Status of the SSH connection.
            cloud_package (str): The cloud package in use.
            ssh_test_interface (str): The SSH test interface.
            operating_system (str): The operating system of the server.
            cloud_0 (str): Identifier for CloudV 0.
            assert_data (List[str]): A list to append assertion failure messages.
        """
        self.logger.debug("Initiating port status checks.")
        open_ports: Dict[int, bool] = {}
        package_names: Dict[int, str] = {}

        if connection_successful:
            # Execute Python command on the server
            try:
                self.logger.debug(f"Executing Python command: {self.PYTHON_COMMAND}{PYTHON_BINARY}")
                ssh.exec_command(f'{self.PYTHON_COMMAND} "{PYTHON_BINARY}"')
            except Exception as e:
                self.logger.error(f"Failed to execute Python command on the server: {e}")
                assert_data.append(f"Failed to execute Python command: {e}")
                return

            # Check inbound ports
            for port in self.INBOUND_PORTS:
                port_open = self.check_inbound_port(cloud_server_ip, port)
                open_ports[port] = port_open
                package_names[port] = cloud_package

            # Check outbound ports if OS matches
            if ssh_test_interface.lower() == operating_system.lower():
                install_telnet = self.install_package_on_cloud(self.NETCAT_COMMAND, ssh)
                if install_telnet:
                    for port in self.OUTBOUND_PORTS:
                        port_open = self.check_outbound_port(port, ssh)
                        open_ports[port] = port_open
                        package_names[port] = cloud_package

                    combined_data = {
                        port: {
                            'Port Open': open_ports[port],
                            'Cloud Package': package_names[port]
                        } for port in open_ports
                    }

                    self.port_rules(combined_data, cloud_0, assert_data)
                else:
                    error_msg = f"{cloud_package} with {operating_system} couldn't install telnet using: {self.NETCAT_COMMAND}."
                    self.logger.error(error_msg)
                    assert_data.append(error_msg)

    def check_if_extra_volume_available(
        self,
        extra_drive_gb: str,
        ssh: paramiko.SSHClient,
        assert_data: List[str],
        operating_system: str,
        cloud_package: str
    ) -> List[str]:
        """
        Checks if an extra volume with the specified size is available on the server.

        Args:
            extra_drive_gb (str): The size of the extra drive in GB.
            ssh (paramiko.SSHClient): The established SSH connection.
            assert_data (List[str]): A list to append assertion failure messages.
            operating_system (str): The operating system of the server.
            cloud_package (str): The cloud package in use.

        Returns:
            List[str]: The updated list of assertion failure messages.
        """
        self.logger.debug("Checking for the availability of an extra volume.")
        try:
            stdin, stdout, stderr = ssh.exec_command(self.LSBLK_COMMAND)
            extra_drive_found = False
            extra_drive_correct_size = False

            extra_drive_size = f"{extra_drive_gb}G"

            for line in stdout:
                parts = line.strip().split()
                if len(parts) == 2 and parts[0].startswith('vd'):
                    if parts[1] == extra_drive_size:
                        extra_drive_found = True
                        extra_drive_correct_size = True
                        break

            if extra_drive_found and extra_drive_correct_size:
                self.logger.info(f"Extra drive with correct size {extra_drive_size} is present.")
            else:
                self.logger.fatal("No extra drive with the correct size is present.")
                assert_data.append(
                    f"{operating_system} with {cloud_package} has no extra drive with the correct size."
                )

        except Exception as e:
            self.logger.fatal(f"Problem while checking extra storage: {e}.")
            assert_data.append(
                f"{operating_system} with {cloud_package} encountered an error while checking extra storage: {e}."
            )
        return assert_data

    def test_ssh_functionality(
        self,
        cloud_server_ip: str,
        username: str,
        password: str,
        cloud_0: str,
        ssh_test_interface: str,
        cloud_package: str,
        operating_system: str,
        extra_volume_size: str,
        ssh_connection_type: str,
        ssh_key_authentication: str,
        password_authentication: str
    ) -> List[str]:
        """
        Tests the SSH functionality by establishing a connection, checking port statuses,
        and verifying the presence of extra storage.

        Args:
            cloud_server_ip (str): The IP address of the cloud server.
            username (str): The SSH username.
            password (str): The SSH password.
            cloud_0 (str): Identifier for CloudV 0.
            ssh_test_interface (str): The SSH test interface.
            cloud_package (str): The cloud package in use.
            operating_system (str): The operating system of the server.
            extra_volume_size (str): The size of the extra volume in GB.
            ssh_connection_type (str): The type of SSH connection (e.g., SSH Key, Password).
            ssh_key_authentication (str): Constant representing SSH Key authentication.
            password_authentication (str): Constant representing Password authentication.

        Returns:
            List[str]: A list of assertion failure messages, empty if no failures.
        """
        self.logger.debug("Starting SSH functionality test.")
        assert_data: List[str] = []
        ssh: Optional[paramiko.SSHClient] = None
        connection_successful: Optional[bool] = None
        error: Optional[str] = None

        # Establish SSH connection
        if ssh_connection_type == ssh_key_authentication:
            connection_successful, ssh, error = self.test_ssh_connection(
                ip_address=cloud_server_ip,
                username=username,
                password=password,
                authenticate_with_key=True
            )
        elif ssh_connection_type == password_authentication:
            connection_successful, ssh, error = self.test_ssh_connection(
                ip_address=cloud_server_ip,
                username=username,
                password=password,
                authenticate_with_key=False
            )
        else:
            error = f"Unsupported SSH connection type: {ssh_connection_type}"
            self.logger.error(error)
            assert_data.append(error)

        if error:
            assert_data.append(error)
        else:
            if connection_successful and ssh:
                self.check_ports(
                    ssh=ssh,
                    cloud_server_ip=cloud_server_ip,
                    connection_successful=connection_successful,
                    cloud_package=cloud_package,
                    ssh_test_interface=ssh_test_interface,
                    operating_system=operating_system,
                    cloud_0=cloud_0,
                    assert_data=assert_data
                )
                self.check_if_extra_volume_available(
                    extra_drive_gb=extra_volume_size,
                    ssh=ssh,
                    assert_data=assert_data,
                    operating_system=operating_system,
                    cloud_package=cloud_package
                )
                ssh.close()
                self.logger.info("SSH connection closed successfully.")

        return assert_data
