import socket
import struct
import time

MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008
GATEWAY_DATA_PORT = 7000


def executar_sensor():
    # 1. Escuta o chamado de descoberta Multicast do Gateway
    sock_desc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_desc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_desc.bind(("", MULTICAST_PORT))

    # Configura o grupo multicast no loopback (para Arch Linux / ambiente local)
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("127.0.0.1")
    sock_desc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("[Fonte] Sensor Continuo ligado e aguardando descoberta...")
    dados, endereco_origem = sock_desc.recvfrom(1024)
    gateway_ip = endereco_origem[0]

    print(
        f"[Fonte] Chamado recebido de {gateway_ip}! Enviando cracha de identificacao..."
    )

    # 2. Envia o crachá de resposta para o Gateway
    cracha = b"ID: sensor_continuo_01 | TYPE: continuo | STATUS: Ativo"
    sock_desc.sendto(cracha, (gateway_ip, GATEWAY_RESPONSE_PORT))
    sock_desc.close()

    # 3. Entra no loop contínuo de envio de dados para o Gateway
    sock_dados = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[Fonte] Descoberta concluida. Iniciando envio continuo de telemetria...")

    try:
        contador = 1
        while True:
            mensagem = f"ID: sensor_continuo_01 | LEITURA: {22.5 + (contador % 5)}C"
            sock_dados.sendto(mensagem.encode("utf-8"), (gateway_ip, GATEWAY_DATA_PORT))
            print(f"[Enviado] {mensagem}")

            contador += 1
            time.sleep(3)  # Envia a cada 3 segundos

    except KeyboardInterrupt:
        print("\n[Fonte] Sensor encerrado pelo usuario.")
    finally:
        sock_dados.close()


if __name__ == "__main__":
    executar_sensor()
