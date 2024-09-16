class ClientAuth:
    def __init__(self, addr=None, port=None, login=None, password=None):
        self._addr = addr
        self._port = port
        self._login = login
        self._password = password

    @classmethod
    def from_auth_file(cls, file_path):
        addr, port, login, password = None, None, None, None
        
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    key, value = line.strip().split(':')
                    if key == 'addr':
                        addr = value
                    elif key == 'port':
                        port = int(value)  
                    elif key == 'login':
                        login = value
                    elif key == 'pass':
                        password = value
                    
            if addr is None or port is None or login is None or password is None:
                raise ValueError("Missing required fields in the auth file")

            return cls(addr=addr, port=port, login=login, password=password)

        except Exception as e:
            print(f"Error reading auth file: {e}")
            raise

    def get_addr(self):
        return self._addr

    def get_port(self):
        return self._port

    def get_login(self):
        return self._login

    def get_password(self):
        return self._password

    def set_addr(self, addr):
        self._addr = addr

    def set_port(self, port):
        self._port = port

    def set_login(self, login):
        self._login = login

    def set_password(self, password):
        self._password = password

"""
if __name__ == "__main__":
    client_auth = Client.from_auth_file('auth')
    print("Auth File Address:", client_auth.get_addr())
    print("Auth File Port:", client_auth.get_port())
    print("Auth File Login:", client_auth.get_login())
    print("Auth File Password:", client_auth.get_password())
"""