import socket
import struct
import time
import threading

MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008
GRPC_PORT = 50051  # Porta onde o servidor gRPC desta fonte vai escutar comandos

# Estado interno da fonte controlável
estado_fonte = {
    "ligado": True,
    "intensidade": 80,  # Ex: intensidade da luz em porcentagem
}


def escutar_descoberta():
    """Fica escutando o chamado de descoberta multicast do Gateway."""
    sock_desc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_desc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_desc.bind(("", MULTICAST_PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("127.0.0.1")
    sock_desc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("[Fonte Controlável] Aguardando chamado de descoberta...")
    dados, endereco_origem = sock_desc.recvfrom(1024)
    gateway_ip = "127.0.0.1"

    print(
        f"[Fonte Controlável] Descoberto! Enviando crachá (Informando porta gRPC {GRPC_PORT})..."
    )

    # Informa no crachá que é controlável e passa a porta do gRPC
    cracha = f"ID: poste_luz_03 | TYPE: poste | PORT: {GRPC_PORT} | CONTROLABLE: True".encode(
        "utf-8"
    )
    sock_desc.sendto(cracha, (gateway_ip, GATEWAY_RESPONSE_PORT))
    sock_desc.close()


def enviar_dados_periodicos():
    """Envia o estado atual do atuador periodicamente via UDP para o Gateway."""
    sock_dados = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gateway_ip = "127.0.0.1"

    print("[Fonte Controlável] Iniciando envio periódico de status via UDP...")
    try:
        while True:
            # Envia o estado atual (se está ligado e a intensidade da luz)
            status_msg = f"ID: poste_luz_03 | LIGADO: {estado_fonte['ligado']} | INTENSIDADE: {estado_fonte['intensidade']}".encode(
                "utf-8"
            )
            sock_dados.sendto(status_msg, (gateway_ip, 7000))
            time.sleep(5)
    except Exception as e:
        print(f"[Fonte Controlável] Erro no envio: {e}")
    finally:
        sock_dados.close()


if __name__ == "__main__":
    # Executa a descoberta e depois dispara o envio de dados em segundo plano (thread)
    escutar_descoberta()

    thread_dados = threading.Thread(target=enviar_dados_periodicos, daemon=True)
    thread_dados.start()

    print("[Fonte Controlável] Servidor ativo e rodando. Pressione Ctrl+C para sair.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Fonte Controlável] Desligando...")
