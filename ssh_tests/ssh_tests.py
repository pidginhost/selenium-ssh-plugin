import time

import paramiko
from utilities.utils import Utils
import socket
from contextlib import closing
from ssh_tests.listen_inbound_ports_binary import PYTHON_BINARY


class SSHConnection:
    CLOUD_0_INBOUND_CLOSE_PORT = 1000
    INBOUND_PORTS = [22, 443, 80, 1000]
    OUTBOUND_PORTS = [25, 587, 467]
    NETCAT_COMMAND = "sudo apt-get install -y netcat-traditional"
    PYTHON_COMMAND = "sudo python3 -c "
    LSBLK_COMMAND = "lsblk -o NAME,SIZE"
    EXTRA_STORAGE_NAME1 = "vdb"
    EXTRA_STORAGE_NAME2 = "vdc"
    NC_COMMAND = "nc -z smtp.mail.yahoo.com"

    def __init__(self, private_key_file):
        self.utils = Utils()
        self.private_key_file = private_key_file

    def install_package_on_cloud(self, package_command, ssh_connection):
        retry_count = 30
        for _ in range(retry_count):
            time.sleep(3)
            try:
                stdin, stdout, stderr = ssh_connection.exec_command(package_command)
                # Check if the installation was successful based on the return code
                return_code = stdout.channel.recv_exit_status()
                if return_code == 0:
                    self.utils.custom_logger().info(f"{package_command} : installation successful")
                    return True
                else:
                    error_output = stderr.read().decode('utf-8').strip()
                    self.utils.custom_logger().error(f"Error installing {package_command}: {error_output}")
            except Exception as e:
                self.utils.custom_logger().error(f"Error installing {package_command}: {e}")
            self.utils.custom_logger().error(f"Rentry .... {package_command}")
        self.utils.custom_logger().info(f"{package_command} : installation failed")
        return False

    def check_inbound_port(self, remote_ip, port) -> bool:
        result: bool = True
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(5)
            if sock.connect_ex((remote_ip, port)) != 0:
                self.utils.custom_logger().fatal(
                    f"Test failed: Unable to connect to {remote_ip} on port {port}")
                result = False
        if result:
            self.utils.custom_logger().info(
                f"Test pass: Connected to {remote_ip} on port {port}")
        return result

    def check_outbound_port(self, port, ssh_connection):
        try:
            telnet_command = f"{self.NC_COMMAND} {port}"
            stdin, stdout, stderr = ssh_connection.exec_command(telnet_command)
            return_code = stdout.channel.recv_exit_status()

            if return_code == 0:
                self.utils.custom_logger().info(f"Port {port} is open on smtp.mail.yahoo.com")
                return True
            else:
                self.utils.custom_logger().info(f"Port {port} is closed on smtp.mail.yahoo.com")
                return False
        except Exception as e:
            self.utils.custom_logger().info(f"Error checking port: {e}")
            return False

    def test_ssh_connection(self, ip_address, username, password, authenticate_with_key):
        connection_params = {
            "hostname": ip_address,
            "username": username,
            "channel_timeout": 200,
            "banner_timeout": 200,
            "timeout": 200,
            "auth_timeout": 200
        }
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if authenticate_with_key:
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                connection_params["pkey"] = private_key
            else:
                connection_params["password"] = password
            ssh.connect(**connection_params)
            self.utils.custom_logger().info(
                f"Successfully connected to the server at {ip_address} with "
                f"{'SSH KEY' if authenticate_with_key else 'password'}.")
            return True, ssh
        except paramiko.AuthenticationException:
            self.utils.custom_logger().fatal(
                f"Authentication failed. Incorrect username or {'SSH KEY' if authenticate_with_key else 'password'}.")
        except paramiko.SSHException as e:
            self.utils.custom_logger().fatal(
                f"Unable to establish SSH connection with {'SSH KEY' if authenticate_with_key else 'password'}: {e}")
        except Exception as e:
            self.utils.custom_logger().error(f"Error connecting to the server: {e}. Retrying...")
        return False, False

    def port_rules(self, combined_data, cloud_0, assert_data):
        for port, data in combined_data.items():
            port_open_status = data['Port Open']
            cloud_package = data['Cloud Package']

            if port in self.INBOUND_PORTS:
                if cloud_0 in cloud_package:
                    if port == self.CLOUD_0_INBOUND_CLOSE_PORT:
                        if port_open_status:
                            self.utils.custom_logger().fatal(
                                f"Port inbound {port} is open for {cloud_package}")
                            assert_data.append(f"{cloud_package} port {port} is open.")
                        else:
                            self.utils.custom_logger().info(
                                f"Port inbound {port} is closed for {cloud_package}")
                    else:
                        if port_open_status:
                            self.utils.custom_logger().info(
                                f"Port inbound {port} is open for {cloud_package}")
                        else:
                            self.utils.custom_logger().info(
                                f"Port inbound {port} is closed for {cloud_package}")
                            assert_data.append(f"{cloud_package} port {port} is close.")
                else:
                    if port_open_status:
                        self.utils.custom_logger().info(
                            f"Port inbound {port} is open for {cloud_package}")
                    else:
                        self.utils.custom_logger().fatal(
                            f"Port inbound {port} is closed for {cloud_package}")
                        assert_data.append(f"{cloud_package} port {port} is closed.")
            elif port in self.OUTBOUND_PORTS:
                if port_open_status:
                    self.utils.custom_logger().fatal(
                        f"Port outbound :{port} is open for {cloud_package}")
                    assert_data.append(f"{cloud_package} port {port} is open.")
                else:
                    self.utils.custom_logger().info(
                        f"Port outbound :{port} is closed for {cloud_package}")

    def check_ports(self, ssh, cloud_server_ip, connection_successful, cloud_package,
                    ssh_test_interface, operating_system, cloud_0, assert_data):
        open_ports = {}
        package_names = {}

        if connection_successful:
            ssh.exec_command(f'{self.PYTHON_COMMAND} "{PYTHON_BINARY}"')
            for port in self.INBOUND_PORTS:
                port_open = self.check_inbound_port(cloud_server_ip, port)
                open_ports[port] = port_open
                package_names[port] = cloud_package

            # Test outbound ports limited to Ubuntu packages only.
            if ssh_test_interface == operating_system:
                install_telnet = self.install_package_on_cloud(self.NETCAT_COMMAND, ssh)
                if install_telnet:
                    for port in self.OUTBOUND_PORTS:
                        port_open = self.check_outbound_port(port, ssh,)
                        open_ports[port] = port_open
                        package_names[port] = cloud_package
                    combined_data = {port: {'Port Open': open_ports[port], 'Cloud Package': package_names[port]} for
                                     port in
                                     open_ports}

                    self.port_rules(combined_data, cloud_0, assert_data)
                else:
                    assert_data.append(
                        f"{cloud_package} with {operating_system} can't install telnet with : {self.NETCAT_COMMAND}.")

    def check_if_extra_volume_available(self, extra_drive_gb, ssh, assert_data, operating_system, cloud_package):
        try:
            stdin, stdout, stderr = ssh.exec_command("lsblk -o NAME,SIZE")
            extra_drive_found = False
            extra_drive_correct_size = False

            extra_drive_size = str(extra_drive_gb) + "G"

            for line in stdout:
                parts = line.split()
                if len(parts) == 2 and parts[0].startswith('vd'):
                    if parts[1] == extra_drive_size:
                        extra_drive_found = True
                        extra_drive_correct_size = True
                        break

            if extra_drive_found and extra_drive_correct_size:
                self.utils.custom_logger().info(
                    f"The extra drive with correct size {extra_drive_size} is present.")
            else:
                self.utils.custom_logger().fatal("No extra drive with the correct size is present.")
                assert_data.append(
                    f"{operating_system} with {cloud_package} no extra drive with correct size is present.")

        except Exception as e:
            self.utils.custom_logger().fatal(f"Problem while trying to check the extra storage with error: {e}.")
            assert_data.append(
                f"{operating_system} with {cloud_package} problem while trying to check the extra storage with error: {e}.")
        return assert_data

    def test_ssh_functionality(self, cloud_server_ip, username, password, cloud_0,
                               ssh_test_interface, cloud_package,
                               operating_system, extra_volume_size):
        assert_data = []
        # Test connection by SSH KEY
        connection_successful_with_ssh_key, ssh = self.test_ssh_connection(cloud_server_ip, username, password, True)
        if connection_successful_with_ssh_key:
            ssh.close()
        else:
            assert_data.append(f"{operating_system} with {cloud_package} can't connect with ssh key.")
        # Test connection by password
        connection_successful_with_password, ssh = self.test_ssh_connection(cloud_server_ip, username, password, False)
        if connection_successful_with_password:
            self.check_ports(ssh, cloud_server_ip, connection_successful_with_password, cloud_package,
                             ssh_test_interface, operating_system, cloud_0, assert_data)
            self.check_if_extra_volume_available(extra_volume_size, ssh,
                                                 assert_data, operating_system, cloud_package)
            ssh.close()

        else:
            assert_data.append(f"{operating_system} with {cloud_package} can't connect with password.")

        return assert_data
