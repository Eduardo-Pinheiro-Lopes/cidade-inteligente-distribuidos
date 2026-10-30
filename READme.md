# Sistema Distribuído de Monitoramento IoT para Cidades Inteligentes

Trabalho prático desenvolvido para a disciplina de Sistemas Distribuídos na **Universidade Federal do Ceará (UFC)**. O projeto implementa uma arquitetura distribuída voltada para o contexto de Smart Cities, integrando descoberta dinâmica de nós, transmissão de dados em tempo real, tolerância a eventos críticos e controle remoto de atuadores.

---

## Arquitetura do Sistema

O sistema é composto por três blocos principais desacoplados que se comunicam através de protocolos de rede de baixo nível:

1. **Gateway Central (`/gateway`):** Atua como o núcleo do sistema. Responsável por iniciar a descoberta de nós via UDP Multicast, centralizar leituras e alertas em threads paralelas, fornecer um servidor gRPC/TCP de controle e atender as requisições dos operadores.
2. **Fontes de Dados / Dispositivos (`/sources`):** Simulam sensores e atuadores urbanos heterogêneos:
   - *Sensor Contínuo (`sensor_continous.py`):* Envia métricas periódicas.
   - *Sensor com Alerta (`sensor_com_alerta.py`):* Monitora limiares e dispara pacotes imediatos em caso de anomalias.
   - *Fonte Controlável (`fonte_controlavel.py`):* Atuador híbrido que envia status via UDP e expõe serviços para controle remoto.
3. **Cliente CLI (`/client`):** Interface de linha de comando baseada em TCP para que operadores consultem o estado da rede e interajam com o sistema em tempo real.

---

## Estrutura do Repositório

```text
Cidade_Inteligente/
├── proto/
│   └── city.proto              # Contratos e definições de mensagens Protobuf
├── gateway/
│   └── gateway_server.py       # Servidor central (Descoberta, UDP e TCP)
├── sources/
│   ├── sensor_continous.py     # Fonte 1: Sensor periódico padrão
│   ├── sensor_com_alerta.py    # Fonte 2: Sensor com disparo de evento por limiar
│   └── fonte_controlavel.py    # Fonte 3: Atuador com suporte a gRPC
├── client/
│   └── client_cli.py           # Cliente CLI para interação do operador
└── README.md
