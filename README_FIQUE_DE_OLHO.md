# Template "Fique de Olho!" 📢

Novo template para geração de boletins informativos com design moderno e layout responsivo.

## 🎨 Características

- **Design moderno** com fundo escuro semi-transparente
- **Layout responsivo** otimizado para mobile e desktop
- **Logo personalizável** (public/logo.jpg)
- **Flags/emojis opcionais** para categorizar notícias
- **Lista dinâmica** de notícias
- **Footer corporativo** (@granelcorretora)

## 📋 Campos de Dados

### Obrigatórios:
- `dia_semana`: String com o dia da semana (ex: "Segunda-feira")
- `lista_noticias`: Array de objetos com notícias

### Opcionais:
- `titulo_customizado`: Título personalizado (padrão: "Fique de Olho!")

### Estrutura da lista de notícias:
```json
{
  "flag": "🇧🇷",           // Emoji/flag opcional
  "texto": "Notícia aqui"  // Texto da notícia (obrigatório)
}
```

## 📄 Exemplo de Uso

```json
{
  "template_name": "fique_de_olho",
  "data": {
    "dia_semana": "Segunda-feira",
    "lista_noticias": [
      {
        "flag": "🇧🇷",
        "texto": "Mercado brasileiro em alta"
      },
      {
        "flag": "🌎",
        "texto": "Commodities internacionais estáveis"
      },
      {
        "flag": "📈",
        "texto": "Soja com expectativa de crescimento"
      },
      {
        "texto": "Notícia sem bandeira exemplo"
      }
    ]
  },
  "output_format": "png",
  "upload_to_minio": true
}
```

## 🎯 Formatos Suportados

- ✅ **PDF** - ReportLab (compatível Windows)
- ✅ **PNG** - PIL (geração direta)
- ✅ **JPEG** - PIL (geração direta)
- ✅ **MinIO Upload** - URLs públicas

## 🚀 Como Testar

```bash
# Teste completo do template
python test_fique_de_olho.py

# Teste rápido via API
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "fique_de_olho",
    "data": {
      "dia_semana": "Hoje",
      "lista_noticias": [
        {"flag": "⚡", "texto": "Teste rápido funcionando!"}
      ]
    },
    "output_format": "png",
    "upload_to_minio": false
  }'
```

## 🎨 Personalização

### Logo:
- Coloque sua logo em `public/logo.jpg`
- Formato recomendado: Quadrado (1:1)
- Tamanho: 70x70px

### Cores:
- Fundo: rgba(0,0,0,0.75)
- Texto: Branco (#ffffff)
- Barra verde: #2e7d32
- Pontos ativos: #2947a9
- Pontos inativos: #b0b7c3

## 💡 Casos de Uso

- 📰 **Boletins de mercado**
- 📊 **Newsletters corporativas**
- 📱 **Informativos para redes sociais**
- 📧 **Comunicados por email**
- 🏢 **Relatórios executivos**

## ✨ Vantagens

- ✅ Sem dependências externas (Poppler)
- ✅ Funciona 100% no Windows
- ✅ Design profissional
- ✅ Geração rápida
- ✅ Upload automático para MinIO
- ✅ URLs públicas para compartilhamento
- ✅ Responsivo para diferentes tamanhos

---

**💼 Desenvolvido para Granel Corretora**  
Template otimizado para comunicação corporativa moderna e eficiente. 