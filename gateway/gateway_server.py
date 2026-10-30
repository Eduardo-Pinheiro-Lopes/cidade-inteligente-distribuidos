import socket
import struct
import threading
import time

MULTICAST_GROUP = '239.255.255.250'
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008
GATEWAY_DATA_PORT = 7000
GATEWAY_TCP_PORT = 8000

# Dicionário para armazenar as fontes cadastradas
fontes_cadastradas = {}

def escutar_dados_fontes():
    """Thread dedicada a receber leituras contínuas, alertas e status via UDP das fontes."""
    sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_data.bind(('', GATEWAY_DATA_PORT))
    
    print(f"[Gateway] Ouvindo dados e alertas na porta UDP {GATEWAY_DATA_PORT}...")
    
    try:
        while True:
            dados, origem = sock_data.recvfrom(1024)
            mensagem = dados.decode('utf-8')
            print(f"[Gateway - Dados Recebidos de {origem[0]}] -> {mensagem}")
    except Exception as e:
        print(f"[Gateway] Erro no recebimento de dados: {e}")
    finally:
        sock_data.close()

def loop_descoberta_continua():
    """Envia sinais de descoberta periodicamente para encontrar novas fontes a qualquer momento."""
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack('b', 1)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    
    try:
        while True:
            sock_envio.sendto(b"DISCOVER_SOURCES", (MULTICAST_GROUP, MULTICAST_PORT))
            time.sleep(5)
    except Exception as e:
        print(f"[Gateway] Erro no envio de descoberta: {e}")
    finally:
        sock_envio.close()

def ouvir_respostas_descoberta():
    """Escuta continuamente as respostas (crachás) das fontes na rede."""
    sock_escuta = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_escuta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_escuta.bind(('', GATEWAY_RESPONSE_PORT))
    
    print(f"[Gateway] Escutando respostas de descoberta na porta {GATEWAY_RESPONSE_PORT}...")
    
    try:
        while True:
            dados, origem = sock_escuta.recvfrom(1024)
            cracha_msg = dados.decode('utf-8')
            
            if origem[0] not in fontes_cadastradas:
                print(f"[Gateway] Nova fonte descoberta! IP: {origem[0]} | Info: {cracha_msg}")
            
            fontes_cadastradas[origem[0]] = cracha_msg
    except Exception as e:
        print(f"[Gateway] Erro ao escutar respostas: {e}")
    finally:
        sock_escuta.close()

def servidor_tcp_gateway():
    """Gerencia as conexões TCP dos clientes que consultam o sistema."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', GATEWAY_TCP_PORT))
    server_sock.listen(5)
    
    print(f"[Gateway] Servidor TCP ouvindo conexões na porta {GATEWAY_TCP_PORT}...")
    
    try:
        while True:
            client_conn, client_addr = server_sock.accept()
            print(f"[Gateway] Novo cliente conectado via TCP: {client_addr}")
            
            while True:
                requisicao = client_conn.recv(1024)
                if not requisicao:
                    break
                
                msg = requisicao.decode('utf-8')
                
                if msg == "LIST_SOURCES":
                    if fontes_cadastradas:
                        resposta_str = "\n".join([f"- IP {ip}: {info}" for ip, info in fontes_cadastradas.items()])
                    else:
                        resposta_str = "Nenhuma fonte registrada no momento."
                    client_conn.sendall(resposta_str.encode('utf-8'))
                    
                elif msg.startswith("GET_DATA:"):
                    sensor_id = msg.split(":")[1]
                    client_conn.sendall(f"Últimos dados registrados para {sensor_id}: [Ativo no sistema]".encode('utf-8'))
                else:
                    client_conn.sendall(b"Comando desconhecido.")
                    
            client_conn.close()
    except Exception as e:
        print(f"[Gateway] Erro no servidor TCP: {e}")
    finally:
        server_sock.close()

def iniciar_gateway():
    print("[Iniciando Gateway Central com Descoberta Contínua...]")
    
    threading.Thread(target=escutar_dados_fontes, daemon=True).start()
    threading.Thread(target=ouvir_respostas_descoberta, daemon=True).start()
    threading.Thread(target=loop_descoberta_continua, daemon=True).start()
    threading.Thread(target=servidor_tcp_gateway, daemon=True).start()
    
    print("[Gateway] Sistema totalmente operacional. Pressione Ctrl+C para encerrar.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Gateway] Encerrando o Gateway Central.")

if __name__ == "__main__":
    iniciar_gateway()
