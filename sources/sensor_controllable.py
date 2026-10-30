import socket
import struct
import time
import threading

MULTICAST_GROUP = "239.255.255.250"
MULTICAST_PORT = 5007
GATEWAY_RESPONSE_PORT = 5008
GATEWAY_DATA_PORT = 7000
CONTROL_PORT = 6001  # Porta onde este atuador escuta comandos de controle

# Estado interno do atuador (pode ser alterado remotamente)
estado_atuador = {
    "id": "atuador_poste_01",
    "ligado": True,
    "intensidade": 80,  # Ex: 80% de luminosidade
}


def escutar_comandos_controle():
    """Servidor TCP interno da fonte para receber comandos de controle remoto."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", CONTROL_PORT))
    server_sock.listen(1)

    print(f"[Atuador] Servidor de controle pronto na porta {CONTROL_PORT}...")

    try:
        while True:
            conn, addr = server_sock.accept()
            dados = conn.recv(1024)
            if dados:
                comando = dados.decode("utf-8").strip()
                print(f"[Atuador] Comando recebido de {addr}: {comando}")

                # Processa o comando de controle
                if comando == "TOGGLE":
                    estado_atuador["ligado"] = not estado_atuador["ligado"]
                    resposta = f"SUCESSO: Estado alterado para Ligado={estado_atuador['ligado']}"
                elif comando.startswith("SET_INTENSITY:"):
                    try:
                        valor = int(comando.split(":")[1])
                        estado_atuador["intensidade"] = max(0, min(100, valor))
                        resposta = f"SUCESSO: Intensidade ajustada para {estado_atuador['intensidade']}%"
                    except ValueError:
                        resposta = "ERRO: Valor inválido para intensidade."
                else:
                    resposta = "ERRO: Comando desconhecido."

                conn.sendall(resposta.encode("utf-8"))
            conn.close()
    except Exception as e:
        print(f"[Atuador] Erro no servidor de controle: {e}")
    finally:
        server_sock.close()


def executar_fonte_controlavel():
    # 1. Escuta o chamado de descoberta Multicast do Gateway
    sock_desc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_desc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_desc.bind(("", MULTICAST_PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("127.0.0.1")
    sock_desc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("[Fonte Controlável] Aguardando chamado de descoberta...")
    dados, endereco_origem = sock_desc.recvfrom(1024)
    gateway_ip = endereco_origem[0]

    print(
        f"[Fonte Controlável] Descoberto por {gateway_ip}! Enviando crachá (Atuador com porta de controle {CONTROL_PORT})..."
    )

    # 2. Envia o crachá informando que é controlável
    cracha = f"ID: {estado_atuador['id']} | TYPE: controlavel | CONTROL_PORT: {CONTROL_PORT}".encode(
        "utf-8"
    )
    sock_desc.sendto(cracha, (gateway_ip, GATEWAY_RESPONSE_PORT))
    sock_desc.close()

    # 3. Inicia o servidor de comandos em uma Thread paralela
    threading.Thread(target=escutar_comandos_controle, daemon=True).start()

    # 4. Loop periódico de envio do status atual do atuador via UDP para o Gateway
    sock_dados = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[Fonte Controlável] Iniciando envio periódico de status...")

    try:
        while True:
            mensagem = f"ID: {estado_atuador['id']} | LIGADO: {estado_atuador['ligado']} | INTENSIDADE: {estado_atuador['intensidade']}%"
            sock_dados.sendto(mensagem.encode("utf-8"), (gateway_ip, GATEWAY_DATA_PORT))
            print(f"[Status Enviado] {mensagem}")
            time.sleep(4)
    except KeyboardInterrupt:
        print("\n[Fonte Controlável] Encerrada pelo usuário.")
    finally:
        sock_dados.close()


if __name__ == "__main__":
    executar_fonte_controlavel()
