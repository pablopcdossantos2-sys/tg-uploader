# TG Uploader

Aplicativo desktop em Python para enviar todos os arquivos de uma pasta local para um grupo do Telegram, com interface gráfica moderna e acompanhamento real do progresso de upload.

> Projeto independente e não oficial. O aplicativo usa a API do Telegram por meio da biblioteca Telethon e não é afiliado ao Telegram.

## O que a primeira versão faz

- interface gráfica moderna com `CustomTkinter`;
- autenticação de uma conta do Telegram por código de verificação e, quando necessário, senha de duas etapas;
- listagem dos grupos acessíveis pela conta conectada;
- seleção de uma pasta local pelo explorador de arquivos;
- opção de incluir ou ignorar subpastas;
- pré-visualização da fila de arquivos antes do envio;
- upload sequencial dos arquivos como documentos;
- porcentagem real do arquivo atual, calculada com os bytes informados pelo `progress_callback` do Telethon;
- progresso total da pasta;
- indicação do arquivo atual, quantidade de arquivos, bytes enviados e velocidade média;
- cancelamento do upload;
- armazenamento da sessão do Telegram e das preferências na pasta de dados do usuário, fora do repositório;
- armazenamento do `API Hash` pelo gerenciador de credenciais do sistema quando disponível via `keyring`.

## Requisitos

- Windows 10 ou Windows 11;
- Python 3.11 ou mais recente recomendado;
- uma conta do Telegram que participe do grupo de destino e tenha permissão para enviar arquivos;
- `api_id` e `api_hash` próprios, criados em <https://my.telegram.org>.

A API do Telegram é oferecida gratuitamente, mas o uso deve respeitar os Termos de Serviço da API. Não use a aplicação para spam, flooding ou automação abusiva.

## 1. Baixar o projeto

Na página do repositório, clique em **Code > Download ZIP**. Extraia o arquivo ZIP para uma pasta fácil de localizar, por exemplo:

```text
C:\Programas\tg-uploader
```

Também é possível clonar com Git:

```powershell
git clone https://github.com/pablopcdossantos2-sys/tg-uploader.git
cd tg-uploader
```

## 2. Criar as credenciais da API do Telegram

1. Acesse <https://my.telegram.org>.
2. Entre com o mesmo número de telefone da conta que será usada pelo programa.
3. Abra **API development tools**.
4. Crie uma aplicação.
5. Guarde os valores **App api_id** e **App api_hash**.

Nunca publique seu `api_hash` em commits, prints ou arquivos enviados para terceiros.

## 3. Preparar o Python no Windows

Abra o **PowerShell** dentro da pasta do projeto. Uma forma simples é abrir a pasta no Explorador, clicar na barra de endereço, digitar `powershell` e pressionar Enter.

Crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o Windows bloquear a ativação do ambiente, você pode instalar as dependências diretamente com `python -m pip install -r requirements.txt`, sem ativar o ambiente.

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Executar

Com o PowerShell ainda aberto na pasta do projeto:

```powershell
python main.py
```

## 5. Primeiro acesso

1. Preencha **API ID**, **API Hash** e o telefone no formato internacional, por exemplo `+5511999999999`.
2. Clique em **Conectar e carregar grupos**.
3. O Telegram enviará um código de verificação para a conta. Digite o código na janela da aplicação.
4. Se a conta possuir verificação em duas etapas, informe também a senha quando solicitada.
5. Escolha o grupo na lista carregada.
6. Selecione a pasta que contém os arquivos.
7. Confira a fila.
8. Clique em **Iniciar upload**.

A sessão autorizada fica armazenada na pasta de dados do usuário. Assim, normalmente não será necessário inserir o código de verificação em toda execução.

## Onde ficam os dados locais

No Windows, a aplicação utiliza aproximadamente esta pasta:

```text
%APPDATA%\TGUploader
```

Nela ficam a sessão do Telethon e as preferências da interface. O `API Hash` é enviado ao `keyring`, que usa o mecanismo de credenciais disponível no sistema operacional.

## Segurança

- Não coloque `api_id`, `api_hash`, códigos de verificação ou senhas no código-fonte.
- Não envie o arquivo de sessão do Telethon a terceiros; ele representa uma sessão autenticada da sua conta.
- Revogue sessões desconhecidas em **Telegram > Configurações > Dispositivos**.
- Use apenas grupos em que a conta tenha autorização para publicar arquivos.

## Estrutura do projeto

```text
tg-uploader/
├── main.py
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── config.py
    ├── telegram_service.py
    └── ui.py
```

## Próximos avanços sugeridos

A arquitetura foi deixada preparada para receber recursos adicionais, como retomada de fila após falha, histórico de uploads, filtros por extensão, limite de velocidade, múltiplos destinos, criação de executável `.exe` com PyInstaller e checksum para evitar reenvio acidental de arquivos já enviados.

## Referências

- Telegram — criação do `api_id` e `api_hash`: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Termos de Serviço da API: <https://core.telegram.org/api/terms>
- Telethon — documentação: <https://docs.telethon.dev/>

## Licença

Ainda não definida. Antes de distribuir versões compiladas publicamente, escolha e adicione uma licença adequada ao repositório.
