import network
import socket
import machine

db={'pin1':0,'pin2':0,'pin3':0,'pin4':0}
# Configure the LED (GPIO 16 is mapped to D0 on NodeMCU)
pin1 = machine.Pin(5, machine.Pin.OUT, value=1)
pin2 = machine.Pin(4, machine.Pin.OUT, value=1)
pin3 = machine.Pin(0, machine.Pin.OUT, value=1)
pin4 = machine.Pin(2, machine.Pin.OUT, value=1)

def update_pins():
    pin1.value(0 if db['pin1']==1 else 1)
    pin2.value(0 if db['pin2']==1 else 1)
    pin3.value(0 if db['pin3']==1 else 1)
    pin4.value(0 if db['pin4']==1 else 1)

def create_ap():
    # Create an Access Point (AP) object
    ap = network.WLAN(network.AP_IF)
    
    # Activate the AP interface
    ap.active(True)
    
    # Set the SSID (name) and password for the AP
    ssid = 'My_MicroPython_AP'
    password = '12345678'
    
    # Configure the AP with the SSID and password
    ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
    
    # Optional: Set the AP's IP address, subnet mask, and gateway
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    
    print('Access Point Created')
    print('SSID:', ssid)
    print('Password:', password)
    print('IP Address:', ap.ifconfig()[0])

# Set up the static IP
def connect_to_network():
    ssid = 'Mob_Pixel 6a'
    password = '2444666668888888'
    
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.ifconfig(('192.168.112.50', '255.255.255.0', '192.168.1.1', '8.8.8.8'))

    if not station.isconnected():
        print('Connecting to network...')
        station.connect(ssid, password)
        while not station.isconnected():
            pass

    print('Network Config:', station.ifconfig())

# Set up the web server
def web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    
    while True:
        conn, addr = s.accept()
        print('Connection from', addr)
        request = conn.recv(1024)
        request_str = str(request)
        # print('Request:', request_str)

        # Parse the query
        if '/api?q=' in request_str:
            try:
                params = request_str.split('/api?q=')[1].split(' ')[0]
                data_sent = params.strip('{').strip('}').split(',')
                
                auth_code=data_sent[0].split(':')[1]
                pin_states=data_sent[1:]
                
                if auth_code=='0000':
                    for i in pin_states:
                        pin=i.split(':')
                        if pin[0]=='pin1':
                            db['pin1']=int(pin[1])
                        elif pin[0]=='pin2':
                            db['pin2']=int(pin[1])
                        elif pin[0]=='pin3':
                            db['pin3']=int(pin[1])
                        elif pin[0]=='pin4':
                            db['pin4']=int(pin[1])
                        

                    update_pins()
                    print(db)
                    response=str(db)
                    
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    conn.close()
                else :
                    response='Invalid Auth Token'
                    conn.send('HTTP/1.1 401 Invalid Auth Token\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    conn.close()
                    


            except:
                response = 'Error parsing request'
        # else:
        #     response = 'Invalid request'

        

# Main function
def main():
    connect_to_network()
    create_ap()
    web_server()
    

    

if __name__ == '__main__':
    main()
