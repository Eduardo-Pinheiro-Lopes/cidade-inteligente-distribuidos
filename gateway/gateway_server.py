import socket
import struct
import threading

MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008
GATEWAY_DATA_PORT = 7000  # Porta onde o Gateway centraliza os dados das fontes

# Dicionário para armazenar as fontes descobertas na rede
fontes_cadastradas = {}


def escutar_dados_fontes():
    """Thread dedicada a receber leituras contínuas, alertas e status via UDP das fontes."""
    sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_data.bind(("", GATEWAY_DATA_PORT))

    print(f"[Gateway] Ouvindo dados e alertas na porta UDP {GATEWAY_DATA_PORT}...")

    try:
        while True:
            dados, origem = sock_data.recvfrom(1024)
            mensagem = dados.decode("utf-8")
            print(f"[Gateway - Dados Recebidos de {origem[0]}] -> {mensagem}")

            # Aqui no futuro faremos o parsing usando Protobuf (SensorReadingMessage)

    except Exception as e:
        print(f"[Gateway] Erro no recebimento de dados: {e}")
    finally:
        sock_data.close()


def iniciar_gateway():
    print("[Iniciando Gateway Central...]")

    # 1. Inicia a thread para escutar os dados contínuos das fontes em segundo plano
    thread_dados = threading.Thread(target=escutar_dados_fontes, daemon=True)
    thread_dados.start()

    # 2. Socket para escutar o "crachá" de resposta das fontes após o Multicast
    sock_escuta = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_escuta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_escuta.bind(("", GATEWAY_RESPONSE_PORT))
    sock_escuta.settimeout(5.0)  # Tempo limite para escutar as respostas

    # 3. Dispara o sinal de descoberta via Multicast
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack("b", 1)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    print("[Gateway] Disparando sinal de descoberta Multicast...")
    sock_envio.sendto(b"DISCOVER_SOURCES", (MULTICAST_GROUP, MULTICAST_PORT))
    sock_envio.close()

    print("[Gateway] Aguardando o 'crachá' de identificação das fontes...")

    try:
        while True:
            dados, origem = sock_escuta.recvfrom(1024)
            cracha_msg = dados.decode("utf-8")
            print(
                f"[Gateway] Fonte registrada com sucesso! IP: {origem[0]} | Info: {cracha_msg}"
            )

            # Armazena na nossa lista central de fontes
            fontes_cadastradas[origem[0]] = cracha_msg

    except socket.timeout:
        print(
            f"[Gateway] Descoberta concluída. Total de fontes ativas registradas: {len(fontes_cadastradas)}"
        )

    sock_escuta.close()

    # Mantém o Gateway rodando para continuar processando os dados recebidos pelas fontes
    print(
        "[Gateway] Sistema central em operação contínua. Pressione Ctrl+C para encerrar."
    )
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n[Gateway] Encerrando o Gateway Central.")


# Adicione esta função no gateway/gateway_server.py e chame-a via Thread
GATEWAY_TCP_PORT = 8000


def servidor_tcp_gateway():
    """Gerencia as conexões TCP dos clientes que consultam o sistema."""
    server_sock = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM
    )  # Ajustado para TCP abaixo:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", GATEWAY_TCP_PORT))
    server_sock.listen(5)

    print(
        f"[Gateway] Servidor TCP ouvindo conexões de clientes na porta {GATEWAY_TCP_PORT}..."
    )


import socket
import struct
import threading
import time

MULTICAST_GROUP = "239.255.255.250"
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
    sock_data.bind(("", GATEWAY_DATA_PORT))

    print(f"[Gateway] Ouvindo dados e alertas na porta UDP {GATEWAY_DATA_PORT}...")

    try:
        while True:
            dados, origem = sock_data.recvfrom(1024)
            mensagem = dados.decode("utf-8")
            print(f"[Gateway - Dados Recebidos de {origem[0]}] -> {mensagem}")
    except Exception as e:
        print(f"[Gateway] Erro no recebimento de dados: {e}")
    finally:
        sock_data.close()


def loop_descoberta_continua():
    """Envia sinais de descoberta periodicamente para encontrar novas fontes a qualquer momento."""
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack("b", 1)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    try:
        while True:
            sock_envio.sendto(b"DISCOVER_SOURCES", (MULTICAST_GROUP, MULTICAST_PORT))
            time.sleep(5)  # Dispara um novo chamado a cada 5 segundos
    except Exception as e:
        print(f"[Gateway] Erro no envio de descoberta: {e}")
    finally:
        sock_envio.close()


def ouvir_respostas_descoberta():
    """Escuta continuamente as respostas (crachás) das fontes na rede."""
    sock_escuta = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_escuta.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_escuta.bind(("", GATEWAY_RESPONSE_PORT))

    print(
        f"[Gateway] Escutando respostas de descoberta na porta {GATEWAY_RESPONSE_PORT}..."
    )

    try:
        while True:
            dados, origem = sock_escuta.recvfrom(1024)
            cracha_msg = dados.decode("utf-8")

            if origem[0] not in fontes_cadastradas:
                print(
                    f"[Gateway] Nova fonte descoberta! IP: {origem[0]} | Info: {cracha_msg}"
                )

            fontes_cadastradas[origem[0]] = cracha_msg
    except Exception as e:
        print(f"[Gateway] Erro ao escutar respostas: {e}")
    finally:
        sock_escuta.close()


def servidor_tcp_gateway():
    """Gerencia as conexões TCP dos clientes que consultam o sistema."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", GATEWAY_TCP_PORT))
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

                msg = requisicao.decode("utf-8")

                if msg == "LIST_SOURCES":
                    if fontes_cadastradas:
                        resposta_str = "\n".join(
                            [
                                f"- IP {ip}: {info}"
                                for ip, info in fontes_cadastradas.items()
                            ]
                        )
                    else:
                        resposta_str = "Nenhuma fonte registrada no momento."
                    client_conn.sendall(resposta_str.encode("utf-8"))

                elif msg.startswith("GET_DATA:"):
                    sensor_id = msg.split(":")[1]
                    client_conn.sendall(
                        f"Últimos dados registrados para {sensor_id}: [Ativo no sistema]".encode(
                            "utf-8"
                        )
                    )
                else:
                    client_conn.sendall(b"Comando desconhecido.")

            client_conn.close()
    except Exception as e:
        print(f"[Gateway] Erro no servidor TCP: {e}")
    finally:
        server_sock.close()


def iniciar_gateway():
    print("[Iniciando Gateway Central com Descoberta Contínua...]")

    # Inicia todas as funcionalidades em Threads paralelas independentes
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
