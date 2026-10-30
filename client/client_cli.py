import socket

GATEWAY_HOST = "127.0.0.1"
GATEWAY_TCP_PORT = 8000  # Porta TCP onde o Gateway vai aceitar conexões dos clientes


def iniciar_cliente():
    print("==========================================")
    print("   CLI CLIENT - SISTEMA DE CIDADE INTELIGENTE")
    print("==========================================")

    try:
        # Cria o socket TCP
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((GATEWAY_HOST, GATEWAY_TCP_PORT))
        print(f"[Cliente] Conectado ao Gateway em {GATEWAY_HOST}:{GATEWAY_TCP_PORT}\n")

        print("Comandos disponíveis:")
        print("  1 - Listar fontes ativas")
        print("  2 - Consultar última leitura de uma fonte")
        print("  3 - Sair")

        while True:
            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == "1":
                client_sock.sendall(b"LIST_SOURCES")
                resposta = client_sock.recv(4096)
                print(f"\n[Resposta do Gateway]:\n{resposta.decode('utf-8')}")

            elif opcao == "2":
                sensor_id = input(
                    "Digite o ID do sensor (ex: sensor_temp_01): "
                ).strip()
                comando = f"GET_DATA:{sensor_id}"
                client_sock.sendall(comando.encode("utf-8"))
                resposta = client_sock.recv(4096)
                print(f"\n[Resposta do Gateway]:\n{resposta.decode('utf-8')}")

            elif opcao == "3":
                print("[Cliente] Encerrando conexão...")
                break
            else:
                print("Opção inválida. Tente novamente.")

        client_sock.close()
    except ConnectionRefusedError:
        print(
            "[Erro] Não foi possível conectar ao Gateway. Verifique se ele está rodando."
        )
    except Exception as e:
        print(f"[Erro] Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    iniciar_cliente()
