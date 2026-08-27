# Podcast de Notícias Automático (100% gratuito)

Pipeline que: coleta notícias via RSS → resume e transforma num bate-papo
entre dois jornalistas (Google Gemini, camada gratuita) → gera áudio MP3
(edge-tts, gratuito) → salva no Google Drive → publica no Spotify via feed
RSS próprio hospedado no GitHub Pages. Roda sozinho todo dia via GitHub
Actions — nenhum serviço pago é necessário.

## Estrutura

```
podcast-noticias/
├── feeds.txt              # lista de feeds RSS (edite para adicionar/remover)
├── fetch_news.py          # coleta as notícias recentes
├── generate_script.py     # resume e gera o roteiro (Google Gemini)
├── tts.py                 # roteiro -> áudio MP3 (edge-tts)
├── upload_drive.py        # envia o MP3 para o Google Drive
├── update_feed.py         # atualiza o feed RSS público do podcast
├── main.py                # orquestra tudo, nessa ordem
├── requirements.txt
├── data/episodes.json     # "banco de dados" dos episódios já publicados
├── docs/                  # servido pelo GitHub Pages (feed.xml + áudios)
└── .github/workflows/podcast.yml   # roda tudo automaticamente todo dia
```

## Configuração (passo a passo)

### 1. Editar `update_feed.py`
Preencha as constantes no topo do arquivo (`PODCAST_TITLE`, `SITE_BASE_URL`
com seu usuário do GitHub, etc.) — são os metadados que aparecem no Spotify.

### 2. Criar o repositório no GitHub
Suba esta pasta para um repositório novo (ex: `podcast-noticias`).

### 3. Ativar o GitHub Pages
No repositório: **Settings → Pages → Source → branch `main`, pasta `/docs`**.
Depois disso sua URL de feed será algo como:
`https://SEU_USUARIO.github.io/podcast-noticias/feed.xml`

### 4. Cadastrar os "Secrets" do repositório
Em **Settings → Secrets and variables → Actions → New repository secret**,
crie:

| Secret | Onde conseguir |
|---|---|
| `GEMINI_API_KEY` | aistudio.google.com → Get API Key (gratuito, sem cartão) |
| `EDGE_TTS_VOICE_ANA` | opcional — nome da voz (padrão: `pt-BR-FranciscaNeural`) |
| `EDGE_TTS_VOICE_BRUNO` | opcional — nome da voz (padrão: `pt-BR-AntonioNeural`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | conteúdo inteiro do JSON da service account |
| `GOOGLE_DRIVE_FOLDER_ID` | ID da pasta do Drive (da URL da pasta) |

Lembre-se de compartilhar a pasta do Drive com o e-mail da service account
(`client_email` dentro do JSON) para o upload funcionar. Os dois secrets de
voz são opcionais — se não cadastrar, o script já usa os valores padrão.

### 5. Rodar manualmente a primeira vez
Na aba **Actions** do repositório → workflow "Gerar episódio do podcast" →
**Run workflow**. Isso vai gerar o primeiro episódio e publicar `feed.xml`.

### 6. Vincular ao Spotify for Podcasters
Em podcasters.spotify.com, crie o podcast e cole a URL do seu `feed.xml`
quando pedir para importar um feed existente. **Isso é feito uma única vez**
— a partir daí, todo novo episódio que o robô publicar no feed aparece
automaticamente no Spotify (pode levar algumas horas para o Spotify
reprocessar o feed a cada episódio novo).

## Rodando localmente (para testar)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat caminho/para/credenciais.json)"
export GOOGLE_DRIVE_FOLDER_ID=...
python main.py
```

(As vozes do edge-tts já têm padrão embutido — só defina
`EDGE_TTS_VOICE_ANA`/`EDGE_TTS_VOICE_BRUNO` se quiser trocar.)

## Personalizações comuns

- **Adicionar/remover feeds RSS:** edite `feeds.txt`, um link por linha.
- **Mudar o horário de publicação:** edite o `cron` em
  `.github/workflows/podcast.yml` (horário em UTC).
- **Mudar os nomes/personalidades dos jornalistas:** edite `SYSTEM_PROMPT`
  em `generate_script.py`.
- **Trocar de vozes:** rode `edge-tts --list-voices | grep pt-BR` para ver
  todas as opções, e troque os secrets `EDGE_TTS_VOICE_ANA` /
  `EDGE_TTS_VOICE_BRUNO`.

## Observação sobre limites (é grátis, mas tem limites)

- **Google Gemini (camada gratuita):** limite de requisições por dia/minuto
  (varia por modelo). Para 1 episódio/dia isso não chega nem perto do
  limite. Se o modelo usado em `generate_script.py` for aposentado, troque
  o nome do modelo — confira as opções atuais em
  ai.google.dev/gemini-api/docs/models.
- **edge-tts:** não é uma API oficial da Microsoft (usa o mesmo serviço do
  Edge/Read Aloud), então pode sofrer mudanças sem aviso — é estável na
  prática, mas não tem garantia contratual como um serviço pago.
- **Google Drive e GitHub Pages/Actions:** gratuitos nesse volume de uso.
