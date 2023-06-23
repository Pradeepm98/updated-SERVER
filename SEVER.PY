import argparse  # Module for parsing command-line arguments
import socket  # Module for socket programming
import sys  # Module for system-specific parameters and functions
from _thread import *  # Module for multi-threading
from decouple import config  # Module for handling configuration variables

try:
    listening_port = 8080  # Default port for the server to listen on
except KeyboardInterrupt:
    print("\n[*] User has requested an interrupt")
    print("[*] Application Exiting.....")
    sys.exit()

parser = argparse.ArgumentParser()  # Create an argument parser object

# Add command-line arguments
parser.add_argument('--max_conn', help="Maximum allowed connections", default=5, type=int)
parser.add_argument('--buffer_size', help="Number of samples to be used", default=8192, type=int)

args = parser.parse_args()  # Parse the command-line arguments
max_connection = args.max_conn  # Maximum allowed connections
buffer_size = args.buffer_size  # Buffer size for receiving data from clients

def start():  # Main program
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        sock.bind(('', listening_port))  # Bind the socket to the specified port
        sock.listen(max_connection)  # Listen for incoming connections
        print("[*] Server started successfully [ %d ]" % listening_port)
    except Exception:
        print("[*] Unable to Initialize Socket")
        print(Exception)
        sys.exit(2)

    while True:
        try:
            conn, addr = sock.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Receive client data
            start_new_thread(conn_string, (conn, data, addr))  # Start a new thread to handle the connection
        except KeyboardInterrupt:
            sock.close()
            print("\n[*] Graceful Shutdown")
            sys.exit(1)

def conn_string(conn, data, addr):
    try:
        print(data)
        first_line = data.split(b'\n')[0]

        url = first_line.split()[1]  # Extract the URL from the first line of the client's request

        http_pos = url.find(b'://')  # Finding the position of "://"
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(b':')

        webserver_pos = temp.find(b'/')
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            port = 80  # Default port for HTTP
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        print(data)
        proxy_server(webserver, port, conn, addr, data)  # Call the proxy server function
    except Exception:
        pass

def proxy_server(webserver, port, conn, addr, data):
    try:
        print(data)

        print("pradeep")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        sock.connect((webserver, port))  # Connect to the web server
        sock.send(data)  # Forward the client's request to the web server

        while 1:
            reply = sock.recv(buffer_size) 
            print("received - start")
            print(reply) # Receive data from the web server
            print("received")
            if len(reply) > 0:
                conn.send(reply)  # Forward the web server's response to the client

                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print("[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar)))

            else:
                break

        sock.close()  # Close the connection to the web server

        conn.close()  # Close the connection to the client
    except socket.error:
        sock.close()
        conn.close()
        print(sock.error)
        sys.exit(1)

if __name__ == "__main__":
    start()  # Start the server
