# TG Uploader

**Leia este README em outros idiomas:** [English](README.en.md) · [Español](README.es.md)

Aplicativo portátil para Windows destinado ao envio de arquivos de uma pasta local para grupos do Telegram, com interface moderna, progresso real, histórico de uploads, prevenção de duplicados e retomada de filas interrompidas.

> Projeto independente e não oficial. O TG Uploader usa a API do Telegram por meio da biblioteca Telethon e não é afiliado ao Telegram.

---

# Para quem só quer usar o programa

Se você **não tem familiaridade com Terminal, PowerShell, Python ou GitHub**, esta é a parte mais importante do README.

Você **não precisa instalar Python** e **não precisa digitar comandos** para usar uma versão portátil já compilada.

## Passo 1 — Baixar a versão portátil

1. Abra a página do projeto no GitHub.
2. Clique na aba **Actions**.
3. Abra a execução mais recente chamada **Build portable Windows app** que esteja marcada com um ícone verde de sucesso.
4. Role a página até a seção **Artifacts**.
5. Clique em **TG-Uploader-Windows-Portable**.
6. O navegador baixará um arquivo compactado `.zip`.

> Se você recebeu a pasta portátil diretamente de outra pessoa, pode ignorar este passo.

## Passo 2 — Extrair o arquivo ZIP

1. Abra a pasta **Downloads** do Windows.
2. Localize o arquivo baixado.
3. Clique nele com o botão direito.
4. Escolha **Extrair Tudo...**.
5. Escolha uma pasta fácil de encontrar, por exemplo:

```text
C:\Programas\TG-Uploader
```

6. Clique em **Extrair**.

Não execute o programa diretamente de dentro do ZIP. Extraia primeiro.

## Passo 3 — Abrir o TG Uploader

Entre na pasta extraída.

Você deverá encontrar um arquivo parecido com:

```text
TG-Uploader.exe
```

Dê dois cliques nele.

O Windows poderá mostrar uma mensagem de segurança porque o executável ainda não possui assinatura digital comercial. Se você confia no arquivo obtido deste repositório, use as opções do próprio Windows para continuar a execução.

---

# Antes do primeiro uso: criar as credenciais do Telegram

O Telegram exige que aplicações que usam sua API possuam duas informações:

- **API ID**
- **API Hash**

Você precisa fazer isso apenas uma vez para a sua conta.

## Se você já possui um App api_id e um App api_hash

Se você já criou uma aplicação no Telegram anteriormente e já possui:

- **App api_id**
- **App api_hash**

**não é necessário criar outra aplicação apenas para usar o TG Uploader.**

Nesse caso:

1. acesse <https://my.telegram.org>;
2. entre com a mesma conta do Telegram;
3. abra **API development tools**;
4. localize o **App api_id** e o **App api_hash** da aplicação que você já controla;
5. copie esses dois valores;
6. no TG Uploader, informe o `App api_id` no campo **API ID** e o `App api_hash` no campo **API Hash**;
7. prossiga normalmente para a autenticação da conta.

Você pode então **pular a etapa de criar uma nova aplicação** descrita abaixo.

> Reutilize apenas credenciais de uma aplicação que pertença a você ou que você esteja autorizado a administrar. Não use credenciais encontradas na internet ou fornecidas por terceiros desconhecidos.

> Não há vantagem em criar várias aplicações do Telegram sem necessidade. Se as suas credenciais atuais são válidas e você tem acesso a elas, normalmente basta reutilizá-las.

## Passo 1 — Entrar no site do Telegram

1. Abra o navegador.
2. Acesse:

<https://my.telegram.org>

3. Digite o número de telefone da sua conta do Telegram.
4. Use o formato internacional.

Exemplo para um número brasileiro:

```text
+55 11 99999-9999
```

5. O Telegram enviará um código para sua conta.
6. Digite esse código no site.

## Passo 2 — Abrir a área de criação da API

Depois de entrar no site:

1. Clique em **API development tools**.
2. Verifique primeiro se já aparecem um **App api_id** e um **App api_hash**.
3. Se esses dados já existirem e pertencerem a uma aplicação sua, você pode reutilizá-los e **não precisa criar uma nova aplicação**.
4. Somente se ainda não existir uma aplicação registrada para você, preencha os campos para criar uma.

Você pode usar, por exemplo:

```text
App title: TG Uploader
Short name: tguploader
Platform: Desktop
```

Os demais campos podem ser preenchidos de maneira simples, desde que o Telegram aceite os valores.

## Passo 3 — Guardar API ID e API Hash

Depois de criar a aplicação, a página mostrará dados parecidos com:

```text
App api_id: 12345678
App api_hash: abcdef1234567890abcdef1234567890
```

Guarde esses dois valores.

Você precisará digitá-los no TG Uploader.

**Não publique seu API Hash em fóruns, prints, vídeos ou commits do GitHub.**

---

# Primeiro uso do TG Uploader

## Passo 1 — Escolher o idioma

No topo da janela, escolha:

- Português (Brasil)
- English
- Español

A escolha ficará salva para as próximas execuções.

Por padrão, a janela principal é aberta **maximizada**, para facilitar a visualização da fila e do progresso.

Os campos nos quais você precisa digitar alguma informação exibem uma dica dentro do próprio campo, com um exemplo ou indicação do valor esperado.

## Passo 2 — Informar os dados da conta

Na seção **1. Conta Telegram**:

1. No campo **API ID**, digite apenas os números recebidos em `my.telegram.org`.
2. No campo **API Hash**, cole o código recebido no mesmo site.
3. No campo **Telefone**, digite seu número em formato internacional.

Depois que você informar **API ID** e **API Hash** pela primeira vez, o TG Uploader os salva localmente. Nas próximas vezes em que o programa for aberto, esses campos serão preenchidos automaticamente — você não precisará digitá-los novamente.

O **API ID** fica em `data/config.json` e o **API Hash** em `data/secrets.json`. Esses arquivos pertencem à sua cópia portátil do programa.

> Se você apagar o conteúdo da pasta `data/` ou usar uma cópia limpa do TG Uploader, será necessário informar as credenciais novamente.

Exemplo:

```text
+5511999999999
```

## Passo 3 — Conectar ao Telegram

Clique em:

**Conectar e carregar grupos**

Na primeira vez, o Telegram enviará um código de verificação.

Uma pequena janela será aberta dentro do próprio TG Uploader.

Digite o código e clique em **Confirmar**.

Se sua conta possuir senha de verificação em duas etapas, outra janela aparecerá solicitando essa senha.

## Passo 4 — Escolher o grupo e, se desejar, um tópico

Depois da conexão, o TG Uploader carregará os grupos disponíveis para a sua conta.

Na seção **2. Destino — grupo e tópico**:

1. Abra a primeira lista.
2. Clique no grupo para o qual deseja enviar os arquivos.
3. Aguarde alguns instantes enquanto o programa verifica se esse grupo possui tópicos.

Se o grupo **não utiliza tópicos**, o campo de tópico ficará desabilitado e mostrará que aquele grupo não possui tópicos.

Se o grupo **utiliza tópicos**, a segunda lista ficará disponível. Nela você poderá escolher:

- **Geral / sem tópico específico**, para enviar ao destino geral do grupo; ou
- um tópico específico, identificado pelo nome e pelo ID.

Exemplo:

```text
Avisos · 1234
```

Se você escolher um tópico específico, todos os arquivos daquela fila serão enviados para esse tópico.

A fila também guarda o tópico escolhido. Portanto, se o upload for interrompido e retomado depois, os arquivos restantes continuarão sendo enviados para o **mesmo tópico original**.

Sua conta precisa ter permissão para enviar arquivos nesse grupo.

> A proteção contra duplicados também leva o tópico em consideração. Um arquivo já enviado ao tópico A ainda poderá ser enviado ao tópico B do mesmo grupo.

## Passo 5 — Escolher a pasta do computador

Na seção **3. Pasta local**:

1. Clique em **Procurar**.
2. Navegue pelas pastas do Windows.
3. Selecione a pasta que contém os arquivos.
4. Clique em **Selecionar pasta**.

A lista dos arquivos encontrados aparecerá no lado direito.

Se quiser incluir também arquivos existentes dentro das subpastas, mantenha ativada a opção:

**Incluir arquivos das subpastas**

## Passo 6 — Conferir a proteção contra duplicados

Por padrão, fica ativada a opção:

**Ignorar arquivos já enviados ao mesmo grupo**

Recomendamos deixá-la ativada.

O programa calcula o SHA-256 de cada arquivo e evita enviar novamente o mesmo conteúdo para o mesmo grupo.

Apenas renomear o arquivo não faz com que ele seja considerado um arquivo diferente.

## Passo 7 — Iniciar o envio

Clique em:

**Iniciar upload**

Durante o envio você verá:

- arquivo atual;
- porcentagem do arquivo;
- progresso total;
- quantidade de arquivos;
- bytes enviados;
- velocidade média.

Você pode clicar em **Cancelar upload** a qualquer momento.

---

# Se o programa fechar ou a internet cair

Não é necessário começar tudo novamente.

O TG Uploader salva a fila no arquivo:

```text
data\tg_uploader.db
```

Ao abrir novamente o programa, o botão:

**Retomar fila interrompida**

ficará disponível quando existir uma fila recuperável.

Arquivos que já terminaram não serão enviados novamente.

## Limitação importante da retomada

A retomada acontece por arquivo.

Exemplo:

- arquivo 1 terminou: não será reenviado;
- arquivo 2 estava em 50% quando caiu a internet: ele recomeçará do início;
- arquivos seguintes continuam pendentes.

Não existe, nesta versão, retomada a partir do byte exato em que um arquivo foi interrompido.

---

# Ver o histórico de uploads

Clique em:

**Ver histórico de uploads**

O programa mostrará registros com informações como:

- data e hora;
- status;
- grupo;
- nome do arquivo;
- tamanho.

O histórico fica armazenado localmente no banco:

```text
data\tg_uploader.db
```

---

# Sobre a pasta data

A pasta:

```text
data\
```

é muito importante.

Ela pode conter:

- configurações;
- idioma escolhido;
- histórico;
- filas pendentes;
- API ID;
- API Hash;
- sessão autenticada do Telegram.

**Não envie essa pasta para outras pessoas.**

Se quiser entregar uma cópia limpa do programa para outra pessoa:

1. feche o TG Uploader;
2. faça uma cópia da pasta inteira do programa;
3. na cópia, apague o conteúdo de `data\`;
4. entregue essa cópia limpa.

A outra pessoa fará a própria autenticação.

---

# Usar o TG Uploader em um pendrive

A aplicação é portátil.

Você pode copiar a pasta inteira:

```text
TG-Uploader
```

para:

- pendrive;
- HD externo;
- SSD externo;
- outra pasta do computador.

Não copie apenas `TG-Uploader.exe`.

A pasta `_internal` também faz parte do programa.

---

# Para quem deseja gerar a versão portátil no próprio computador

Esta seção é voltada para desenvolvimento ou para quem deseja produzir seu próprio executável.

Se você apenas quer usar o programa, **não precisa fazer nada desta seção**.

## Método mais simples: build_portable.bat

### Passo 1 — Instalar o Python

1. Acesse <https://www.python.org/downloads/>.
2. Baixe uma versão recente do Python 3.
3. Abra o instalador.
4. Na primeira tela, marque a opção parecida com:

```text
Add Python to PATH
```

5. Clique em **Install Now**.
6. Aguarde a instalação terminar.

## Passo 2 — Baixar o código do projeto

Na página principal do repositório:

1. clique no botão verde **Code**;
2. clique em **Download ZIP**;
3. abra a pasta Downloads;
4. clique com o botão direito no ZIP;
5. escolha **Extrair Tudo...**.

## Passo 3 — Executar o arquivo de compilação

Dentro da pasta extraída, procure:

```text
build_portable.bat
```

Dê dois cliques.

Uma janela preta aparecerá.

Isso é normal.

Você **não precisa digitar nada**.

O script executará automaticamente:

- preparação do ambiente;
- instalação das bibliotecas;
- verificação do código;
- testes;
- compilação;
- preparação da pasta portátil.

Quando aparecer a mensagem:

```text
Build concluido com sucesso.
```

a versão pronta estará em:

```text
dist\TG-Uploader
```

---

# Executar pelo código-fonte — tutorial para iniciantes

Esta seção utiliza PowerShell.

Você só precisa dela se quiser desenvolver ou testar o código Python diretamente.

## Passo 1 — Abrir o PowerShell já dentro da pasta correta

1. Abra a pasta do projeto no **Explorador de Arquivos**.
2. Clique uma vez na barra de endereço, onde aparece o caminho da pasta.
3. Apague o caminho mostrado.
4. Digite:

```text
powershell
```

5. Pressione **Enter**.

Uma janela azul ou preta será aberta.

Ela já estará apontando para a pasta correta.

Você verá algo parecido com:

```text
PS C:\Users\SeuNome\Downloads\tg-uploader-main>
```

O texto antes do símbolo `>` pode ser diferente no seu computador. Isso é normal.

## Passo 2 — Criar um ambiente virtual

Copie este comando:

```powershell
python -m venv .venv
```

Cole na janela do PowerShell e pressione **Enter**.

Se tudo der certo, normalmente nenhuma mensagem importante aparecerá. Uma nova pasta chamada `.venv` será criada.

## Passo 3 — Ativar o ambiente

Digite:

```powershell
.\.venv\Scripts\Activate.ps1
```

Pressione **Enter**.

Se funcionar, o início da linha passará a mostrar algo parecido com:

```text
(.venv) PS C:\...
```

### Se aparecer erro sobre execução de scripts

Você pode simplesmente pular a ativação e usar os comandos seguintes normalmente com:

```powershell
.\.venv\Scripts\python.exe
```

Por exemplo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Passo 4 — Instalar as bibliotecas

Com o ambiente ativado, execute:

```powershell
python -m pip install --upgrade pip
```

Aguarde terminar.

Depois execute:

```powershell
python -m pip install -r requirements.txt
```

Você verá várias linhas sendo exibidas. Isso é normal.

Espere até o PowerShell voltar a mostrar uma nova linha começando com `PS`.

## Passo 5 — Abrir o programa

Execute:

```powershell
python main.py
```

A janela do TG Uploader deverá aparecer.

---

# Erros comuns

## “python não é reconhecido”

Isso normalmente significa que o Python não foi instalado ou não foi adicionado ao PATH.

Tente:

```powershell
py --version
```

Se funcionar, você pode substituir `python` por `py` nos comandos.

Caso nenhum funcione, reinstale o Python e marque **Add Python to PATH**.

## O PowerShell abriu em outra pasta

Feche a janela e repita:

1. abra a pasta correta no Explorador;
2. clique na barra de endereço;
3. digite `powershell`;
4. pressione Enter.

## O grupo não aparece

Confirme que:

- a conta autenticada participa do grupo;
- a conta possui acesso ao grupo;
- você autenticou a conta correta.

## O botão “Retomar fila interrompida” não aparece

Ele só fica disponível quando existe uma fila incompleta gravada no banco local.

## Um arquivo duplicado não foi enviado

Isso é esperado quando a proteção contra duplicados está ativada.

Se realmente quiser reenviar o arquivo, desative:

**Ignorar arquivos já enviados ao mesmo grupo**

antes de criar uma nova fila.

---

# Estrutura da versão portátil

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

---

# Referências

- Telegram — API ID e API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Termos de Serviço da API: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

# Licença

Ainda não definida. Antes de distribuir releases publicamente, adicione uma licença apropriada ao projeto.
