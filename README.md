# MSM Server

Servidor privado/emulado para o jogo **My Singing Monsters** (Big Blue Bubble). Permite rodar um servidor multiplayer local fora da infraestrutura oficial.

## Componentes

| Componente | Descrição |
|---|---|
| **SFS2X** | SmartFoxServer 2X — servidor de game em tempo real (porta 9933) |
| **auth-server** | Servidor HTTP Python que substitui a autenticação oficial (porta 8080/8082) |
| **sql-server** | Proxy HTTP que traduz queries MySQL para SQLite (porta 8088) |
| **MSMSandbox** | Extensão Java que roda dentro do SFS2X com a lógica do jogo |
| **init_db.py** | Cria e povoa o banco SQLite com dados do jogo (32 tabelas) |
| **export_game_data.py** | Exporta tabelas do jogo para JSON |
| **patch_apk.sh** | Modifica o APK oficial para apontar para seu servidor local |

## Requisitos

- Python 3
- Java 11+ (para o SFS2X)
- Android SDK (`zipalign`, `jarsigner`) — opcional, só para patch do APK

## Setup rápido

```bash
./msm-server/setup.sh         # cria diretórios, inicializa DB, instala dependências
./msm-server/manage.sh start  # inicia SFS2X + auth server
```

## Portas

| Porta | Serviço |
|---|---|
| 9933 | SFS2X Game Server (TCP) |
| 8080/8082 | Auth Server (HTTP) |
| 8088 | SQL Proxy (HTTP) |

## Patch do APK

```bash
./msm-server/patch_apk.sh caminho/do/msm.apk
```

Gera `msm-patched.apk` configurado para conectar em `127.0.0.1:8082`. Instale no Android e faça login.

## Estrutura

```
msm-server/
├── auth-server/        # Autenticação HTTP
├── sql-server/         # Proxy SQL
├── sfs2x/              # SmartFoxServer + extensão MSMSandbox
├── server-data/        # Banco de dados e dados do jogo
├── build/              # Scripts e classes compiladas da extensão Java
├── manage.sh           # Gerenciador de serviços
├── setup.sh            # Setup inicial
├── patch_apk.sh        # Patcher do APK
├── init_db.py          # Inicialização do banco
└── export_game_data.py # Exportação de dados para JSON
```
