# TG Uploader

Aplicativo desktop em Python para enviar arquivos de uma pasta local para um grupo do Telegram, com interface gráfica moderna, acompanhamento real do progresso e suporte a uma **versão portátil para Windows**.

> Projeto independente e não oficial. O aplicativo usa a API do Telegram por meio da biblioteca Telethon e não é afiliado ao Telegram.

## Principais recursos

- interface moderna com `CustomTkinter`;
- autenticação por código de verificação e suporte a senha de duas etapas;
- listagem dos grupos acessíveis pela conta conectada;
- seleção de uma pasta pelo Explorador do Windows;
- opção de incluir ou ignorar subpastas;
- pré-visualização da fila de arquivos;
- upload sequencial dos arquivos como documentos;
- porcentagem real do arquivo atual usando os bytes informados pelo Telethon;
- progresso total da pasta;
- indicação de arquivo atual, quantidade de arquivos, bytes enviados e velocidade média;
- cancelamento do upload;
- sessão persistente;
- **modo portátil**, sem instalador;
- **execução no PC de destino sem Python**, quando usada a versão compilada;
- build portátil por duplo clique em `build_portable.bat`;
- build automático para Windows pelo GitHub Actions.

## Versão portátil

A aplicação foi desenhada para que a versão compilada possa ser copiada como uma pasta independente:

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
└── PORTABLE.md
```

Os dados persistentes são gravados em:

```text
TG-Uploader\data
```

Portanto, a aplicação não depende de `%APPDATA%` para manter a sessão.

A pasta completa pode ser movida para outro diretório, HD externo ou pendrive. O computador de destino **não precisa ter Python instalado**.

Leia também [PORTABLE.md](PORTABLE.md).

## Importante sobre segurança e portabilidade

Para que a sessão continue funcionando ao mover a aplicação, os dados de autenticação precisam acompanhar o executável.

A pasta `data/` pode conter:

- configurações;
- telefone;
- API ID;
- API Hash;
- arquivo de sessão autenticada do Telegram.

Por isso:

**não publique nem compartilhe a pasta `data/`.**

Ela já está incluída no `.gitignore` do projeto.

Se uma cópia portátil contendo sua sessão for perdida ou roubada, revogue essa sessão em **Telegram → Configurações → Dispositivos**.

Para entregar uma cópia limpa da aplicação a outra pessoa, copie a pasta portátil e deixe a pasta `data/` vazia.

## Requisitos para usar a versão portátil pronta

- Windows 10 ou Windows 11;
- acesso à internet;
- uma conta do Telegram que tenha acesso ao grupo de destino;
- `api_id` e `api_hash` próprios, obtidos em <https://my.telegram.org>.

Python **não é necessário** para executar uma versão portátil já compilada.

## Criar as credenciais da API do Telegram

1. Acesse <https://my.telegram.org>.
2. Entre com o número da conta que será usada no TG Uploader.
3. Abra **API development tools**.
4. Crie uma aplicação.
5. Guarde **App api_id** e **App api_hash**.

Nunca publique seu `api_hash`, código de verificação, senha ou arquivo de sessão.

## Opção A — gerar a versão portátil com dois cliques

Esta é a forma recomendada para quem quer produzir o executável localmente.

O computador usado **para compilar** precisa ter Python 3.11 ou mais recente instalado.

Depois de baixar ou clonar o projeto, dê dois cliques em:

```text
build_portable.bat
```

O script cria sozinho um ambiente de compilação, instala as dependências e executa o PyInstaller.

Ao final, a aplicação pronta estará em:

```text
dist\TG-Uploader
```

Copie a pasta `TG-Uploader` inteira. Não copie somente o arquivo `.exe`, porque a versão atual utiliza o formato `onedir` do PyInstaller.

## Opção B — baixar um build gerado pelo GitHub Actions

O repositório contém o workflow:

```text
.github/workflows/build-windows.yml
```

Ele gera o artefato:

```text
TG-Uploader-Windows-Portable
```

O workflow também pode ser iniciado manualmente na aba **Actions** do GitHub.

Essa abordagem permite compilar o programa na infraestrutura do GitHub sem configurar um ambiente de desenvolvimento local.

## Opção C — executar diretamente pelo Python

Para desenvolvimento ou testes, clone o projeto:

```powershell
git clone https://github.com/pablopcdossantos2-sys/tg-uploader.git
cd tg-uploader
```

Crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative-o:

```powershell
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

Mesmo nesse modo, os dados locais são armazenados na pasta `data/` na raiz do projeto. Essa pasta é ignorada pelo Git.

## Primeiro acesso

1. Abra o TG Uploader.
2. Informe **API ID**.
3. Informe **API Hash**.
4. Informe o telefone no formato internacional, por exemplo `+5511999999999`.
5. Clique em **Conectar e carregar grupos**.
6. Digite o código enviado pelo Telegram.
7. Caso exista verificação em duas etapas, informe a senha.
8. Selecione o grupo de destino.
9. Selecione a pasta local.
10. Confira a fila.
11. Clique em **Iniciar upload**.

Depois da primeira autenticação, a sessão é mantida em `data/`, evitando a necessidade de repetir o login a cada execução, enquanto a sessão continuar válida.

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
├── requirements.txt
└── src/
    ├── __init__.py
    ├── config.py
    ├── telegram_service.py
    └── ui.py
```

A pasta `data/` só aparece localmente depois da execução e não deve ser enviada ao GitHub.

## Por que usamos uma pasta portátil em vez de somente um EXE?

O programa é compilado inicialmente com o modo `onedir` do PyInstaller.

Isso oferece algumas vantagens para este projeto:

- inicialização mais previsível;
- melhor compatibilidade com bibliotecas gráficas;
- evita a extração completa da aplicação para uma pasta temporária a cada execução;
- torna mais simples manter a pasta `data/` ao lado da aplicação;
- continua sendo portátil: basta copiar a pasta inteira.

No futuro também podemos oferecer uma variante `onefile`, mas ela não elimina a necessidade de algum armazenamento persistente para a sessão do Telegram.

## Segurança

- Nunca envie a pasta `data/` para o GitHub.
- Nunca compartilhe o arquivo `telegram_session.session`.
- Não publique o API Hash.
- Revogue sessões desconhecidas em **Telegram → Configurações → Dispositivos**.
- Use somente contas e grupos nos quais você tenha autorização para realizar os uploads.
- A API do Telegram deve ser utilizada de acordo com os Termos de Serviço da plataforma.

## Próximos avanços

Alguns recursos previstos para evoluções futuras:

- histórico de uploads;
- identificação de arquivos já enviados;
- retomada de filas interrompidas;
- filtros por extensão;
- logs de falhas;
- checksum para reduzir reenvios acidentais;
- empacotamento de releases assinadas;
- atualização automática opcional.

## Referências

- Telegram — API ID e API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Termos de Serviço da API: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

## Licença

Ainda não definida. Antes de distribuir releases publicamente, escolha e adicione uma licença apropriada ao projeto.
