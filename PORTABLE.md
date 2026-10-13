# TG Uploader — versão portátil

A versão portátil foi projetada para funcionar sem instalador e sem exigir Python no computador do usuário final.

## Como ela funciona

Depois de compilada, a aplicação fica dentro de uma pasta semelhante a esta:

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
└── PORTABLE.md
```

A pasta `data/` é criada e usada ao lado do executável. Nela ficam:

- configurações da interface;
- telefone e API ID;
- API Hash;
- sessão autenticada do Telegram.

Isso significa que a aplicação pode ser copiada para outro diretório, outro disco ou um pendrive junto com a pasta `data/`.

## Criar a versão portátil

No computador usado para compilar, é necessário ter Python instalado apenas uma vez.

A forma mais simples é dar dois cliques em:

```text
build_portable.bat
```

O script:

1. cria um ambiente de compilação isolado;
2. instala as dependências;
3. instala o PyInstaller;
4. gera a aplicação sem janela de terminal;
5. prepara a pasta portátil final.

Ao terminar, a versão pronta estará em:

```text
dist\TG-Uploader
```

Copie a pasta `TG-Uploader` inteira para o computador em que desejar usá-la.

## O computador de destino precisa de Python?

Não.

Depois que a versão portátil estiver compilada, basta abrir:

```text
TG-Uploader.exe
```

## Posso usar em um pendrive?

Sim. Copie a pasta `TG-Uploader` inteira para o pendrive.

O desempenho do banco de sessão e dos arquivos locais pode ser menor em dispositivos USB muito lentos, mas a aplicação não depende de instalação no Windows.

## Segurança importante

A portabilidade exige que os dados necessários também viajem com a aplicação.

A pasta `data/` contém informações sensíveis, especialmente:

- o API Hash;
- a sessão autenticada do Telegram.

**Não publique, envie ou compartilhe a pasta `data/`.**

Quem obtiver a sessão autenticada poderá potencialmente acessar a conta dentro dos limites daquela sessão. Caso a pasta seja perdida ou roubada, revogue a sessão correspondente em:

**Telegram → Configurações → Dispositivos**

## Uma cópia limpa

Se você quiser entregar a aplicação a outra pessoa sem compartilhar sua própria conta:

1. feche o TG Uploader;
2. faça uma cópia da pasta portátil;
3. apague todo o conteúdo da pasta `data/` dessa cópia;
4. entregue apenas a cópia limpa.

Na primeira execução, a outra pessoa poderá configurar suas próprias credenciais e autenticar a própria conta.
