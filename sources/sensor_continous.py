import socket
import struct

MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008


def iniciar_fonte():
    print("[Fonte] Sensor/Atuador ligado e aguardando descoberta...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Vincula à porta do multicast em todas as interfaces locais
    sock.bind(("", MULTICAST_PORT))

    # Força a entrada no grupo multicast usando o endereço local 127.0.0.1
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("127.0.0.1")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        dados, endereco_origem = sock.recvfrom(1024)
        gateway_ip = "127.0.0.1"  # Forçamos o envio para o localhost com segurança

        print(
            f"[Fonte] Chamado recebido! Respondendo para o Gateway em {gateway_ip}:{GATEWAY_RESPONSE_PORT}..."
        )

        resposta_cracha = (
            b"ID: sensor_temp_01 | TYPE: temperatura | PORT: 6001 | CONTROLABLE: False"
        )
        sock.sendto(resposta_cracha, (gateway_ip, GATEWAY_RESPONSE_PORT))
        break


if __name__ == "__main__":
    iniciar_fonte()
