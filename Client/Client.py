import client_lib

def main():
    server=client_lib.client.ClientHandle('127.0.0.1')
    server.run()

if __name__=='__main__':
    main()