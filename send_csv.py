import socket
import time
import sys

host = 'localhost'
port = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
while True:
    print('\nListening for a client at',host , port)
    conn, addr = s.accept()
    print('\nConnected by', addr)
    try:
        print('\nReading file...\n')
        start = time.time()
        with open(str(sys.argv[1])) as f:
            for line in f:
                out = line.encode('utf-8')
                # print('Sending line',line)
                conn.send(out)
                # sleep()
            print('End Of Stream.')
        done = time.time()
        elapsed = done -start
        print(elapsed)
    except socket.error:
        print ('Error Occured.\n\nClient disconnected.\n')
conn.close()