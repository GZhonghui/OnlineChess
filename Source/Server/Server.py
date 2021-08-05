import server_lib

def main():
    server=server_lib.server.ServerHandle('127.0.0.1')
    server.run()

if __name__=='__main__':
    main()