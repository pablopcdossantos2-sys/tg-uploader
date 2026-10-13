# TG Uploader

**Leia este README em outros idiomas:** [English](README.en.md) · [Español](README.es.md)

Aplicativo desktop portátil para Windows, escrito em Python, destinado ao envio de arquivos de uma pasta local para grupos do Telegram, com interface moderna, progresso real, histórico, prevenção de duplicados e retomada de filas interrompidas.

> Projeto independente e não oficial. O TG Uploader usa a API do Telegram por meio da biblioteca Telethon e não é afiliado ao Telegram.

## Recursos

- interface moderna com `CustomTkinter`;
- idiomas **Português (Brasil)**, **English** e **Español**;
- idioma escolhido salvo entre execuções;
- autenticação da conta do Telegram pela própria GUI;
- suporte a código de verificação e senha em duas etapas;
- listagem dos grupos acessíveis pela conta;
- seleção de uma pasta local pelo Explorador do Windows;
- opção de incluir arquivos das subpastas;
- pré-visualização da fila;
- progresso real do arquivo atual;
- progresso total da fila;
- velocidade média de transferência;
- cancelamento do upload;
- **histórico persistente de uploads**;
- **prevenção de arquivos duplicados**;
- **retomada de filas interrompidas**;
- versão **portátil**, sem instalador;
- versão compilada que não exige Python no computador de destino;
- compilação local com `build_portable.bat`;
- compilação automática para Windows com GitHub Actions.

## Histórico de uploads

O programa mantém um histórico local em:

```text
data\tg_uploader.db
```

O banco SQLite registra, entre outras informações:

- data e hora;
- grupo de destino;
- arquivo;
- tamanho;
- hash SHA-256;
- estado do envio;
- identificador da mensagem do Telegram quando disponível.

O histórico pode ser aberto diretamente pela GUI em **Ver histórico de uploads**.

## Prevenção de duplicados

Por padrão, a opção:

**Ignorar arquivos já enviados ao mesmo grupo**

fica ativada.

Antes do upload, o TG Uploader calcula o **SHA-256** do arquivo e consulta o histórico.

Um arquivo é considerado duplicado quando:

1. possui o mesmo conteúdo, isto é, o mesmo SHA-256; e
2. já foi enviado anteriormente para o mesmo grupo.

Isso significa que apenas renomear um arquivo não faz com que ele seja reenviado.

O mesmo arquivo ainda pode ser enviado normalmente para outro grupo.

Se for necessário reenviar deliberadamente um arquivo idêntico para o mesmo grupo, desative a opção de prevenção de duplicados antes de criar uma nova fila.

## Retomada de filas interrompidas

A fila é registrada em SQLite antes do início do envio.

Depois de cada arquivo, seu estado é atualizado. Portanto, se o programa for fechado, o computador for reiniciado ou a conexão falhar:

- arquivos já concluídos permanecem concluídos;
- duplicados já ignorados permanecem concluídos;
- arquivos pendentes continuam pendentes;
- o arquivo que estava sendo transmitido volta para o estado pendente;
- arquivos com falha podem ser tentados novamente.

Na próxima execução, o botão **Retomar fila interrompida** fica disponível quando existir uma fila recuperável.

### Limitação importante

A retomada ocorre **por arquivo**, e não no meio dos bytes de um arquivo.

Se um arquivo de 2 GB for interrompido após 1 GB, esse arquivo específico será iniciado novamente desde o começo. Os arquivos anteriores da fila não serão reenviados.

## Idiomas

O idioma pode ser alterado no cabeçalho da aplicação:

- Português (Brasil);
- English;
- Español.

A preferência é gravada em `data/config.json`.

## Versão portátil

A distribuição compilada possui aproximadamente esta estrutura:

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
├── README.en.md
├── README.es.md
└── PORTABLE.md
```

A pasta inteira pode ser movida para outro diretório, HD externo ou pendrive.

O computador de destino **não precisa ter Python instalado**.

Leia também [PORTABLE.md](PORTABLE.md).

## Dados portáteis e segurança

A pasta `data/` acompanha o programa e pode conter:

- configurações;
- histórico e filas;
- API ID;
- API Hash;
- sessão autenticada do Telegram.

**Não compartilhe nem publique a pasta `data/`.**

Ela já está incluída no `.gitignore`.

Se uma cópia contendo sua sessão for perdida, revogue a sessão em:

**Telegram → Configurações → Dispositivos**

Para entregar uma cópia limpa a outra pessoa, distribua a aplicação com a pasta `data/` vazia.

## Requisitos da versão portátil pronta

- Windows 10 ou Windows 11;
- acesso à internet;
- uma conta do Telegram com acesso ao grupo de destino;
- `api_id` e `api_hash` próprios obtidos em <https://my.telegram.org>.

Python não é necessário no computador que executará uma versão já compilada.

## Criar as credenciais do Telegram

1. Acesse <https://my.telegram.org>.
2. Entre com a conta que será usada pelo TG Uploader.
3. Abra **API development tools**.
4. Crie uma aplicação.
5. Guarde **App api_id** e **App api_hash**.

Nunca publique seu API Hash, código de verificação, senha ou arquivo de sessão.

## Gerar a versão portátil com dois cliques

O computador usado para compilar precisa ter Python 3.11 ou mais recente.

Depois de baixar ou clonar o repositório, execute:

```text
build_portable.bat
```

Ao final, a aplicação estará em:

```text
dist\TG-Uploader
```

Copie a pasta `TG-Uploader` inteira.

## Compilar pelo GitHub Actions

O workflow:

```text
.github/workflows/build-windows.yml
```

gera o artefato:

```text
TG-Uploader-Windows-Portable
```

Ele também pode ser iniciado manualmente na aba **Actions** do GitHub.

## Executar pelo código-fonte

Clone o projeto:

```powershell
git clone https://github.com/pablopcdossantos2-sys/tg-uploader.git
cd tg-uploader
```

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Execute:

```powershell
python main.py
```

## Primeiro uso

1. Abra o TG Uploader.
2. Escolha o idioma desejado.
3. Informe **API ID**.
4. Informe **API Hash**.
5. Informe o telefone em formato internacional.
6. Clique em **Conectar e carregar grupos**.
7. Digite o código enviado pelo Telegram.
8. Informe a senha em duas etapas, se aplicável.
9. Escolha o grupo.
10. Selecione a pasta local.
11. Confira a fila.
12. Mantenha ou desative a proteção contra duplicados.
13. Clique em **Iniciar upload**.

## Estrutura do projeto

```text
tg-uploader/
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── build_portable.bat
├── main.py
├── PORTABLE.md
├── README.md
├── README.en.md
├── README.es.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── config.py
    ├── i18n.py
    ├── storage.py
    ├── telegram_service.py
    └── ui.py
```

## Referências

- Telegram — API ID e API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Termos de Serviço da API: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

## Licença

Ainda não definida. Antes de distribuir releases publicamente, adicione uma licença apropriada ao projeto.
