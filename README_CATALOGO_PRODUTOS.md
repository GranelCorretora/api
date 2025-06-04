# Template "Catálogo de Produtos" 📦

Template moderno para geração de catálogos de produtos organizados por fabricante.

## 🎨 Características

- **Design responsivo** com cards modernos
- **Organização por fabricante**
- **Suporte a imagens** de produtos
- **Preços formatados** automaticamente
- **Categorias e unidades** destacadas
- **Layout adaptativo** para mobile e desktop

## 📋 Estrutura de Dados

### Obrigatórios:
- `catalogo_fabricantes`: Array de objetos com fabricantes e seus produtos

### Opcionais:
- `data_geracao`: Data/hora de geração do catálogo
- `ano_atual`: Ano para o copyright

### Estrutura do catálogo:
```json
{
  "catalogo_fabricantes": [
    {
      "nome_fabricante": "NOME DO FABRICANTE",
      "produtos": [
        {
          "codigo_produto": "123456",
          "nome_produto": "Nome do Produto",
          "preco_sugerido_reais": 99.99,
          "unidade": "UN",
          "descricao_curta": "Descrição breve do produto",
          "url_imagem_placeholder": "URL da imagem",
          "categoria": "Categoria (opcional)"
        }
      ]
    }
  ]
}
```

## 📄 Exemplo de Uso

```python
catalogo_data = {
    "template_name": "catalogo_produtos",
    "data": {
        "data_geracao": "15/03/2024 14:30",
        "ano_atual": "2024",
        "catalogo_fabricantes": [
            {
                "nome_fabricante": "MULTILASER",
                "produtos": [
                    {
                        "codigo_produto": "035734",
                        "nome_produto": "ESCOVA DE DENTE SOFT C/ LIMPADOR DE LÍN. HC591 2UND",
                        "preco_sugerido_reais": 6.06,
                        "unidade": "2UN",
                        "descricao_curta": "Escova de dente macia com limpador de língua.",
                        "url_imagem_placeholder": "https://placehold.co/300x200/e0e0e0/777777?text=Escovas+HC591"
                    }
                ]
            }
        ]
    },
    "output_format": "pdf",
    "upload_to_minio": true
}
```

## 🎯 Formatos Suportados

- ✅ **PDF** - Ideal para impressão
- ✅ **PNG** - Perfeito para web
- ✅ **JPEG** - Otimizado para email
- ✅ **MinIO Upload** - Compartilhamento fácil

## 🚀 Como Testar

```bash
# Teste completo do template
python test_catalogo_produtos.py

# Teste rápido via API
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d @exemplo_catalogo.json
```

## 🎨 Personalização

### Imagens:
- Use URLs públicas para as imagens
- Tamanho recomendado: 300x200px
- Suporte a placeholder images

### Cores:
- Principal: #2196F3 (azul)
- Secundária: #FFC107 (amarelo)
- Texto: #333333
- Fundo: #f5f5f5
- Cards: #ffffff

## 💡 Casos de Uso

- 📱 **Catálogos digitais**
- 📊 **Listas de preços**
- 🏷️ **Apresentações comerciais**
- 📦 **Catálogos de distribuidores**
- 🛍️ **E-commerce**

## ✨ Vantagens

- ✅ Design responsivo
- ✅ Organização intuitiva
- ✅ Formatação automática de preços
- ✅ Suporte a categorias
- ✅ Unidades destacadas
- ✅ Imagens otimizadas
- ✅ Geração rápida

## 📋 Campos do Produto

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| codigo_produto | string | Sim | Código único do produto |
| nome_produto | string | Sim | Nome completo do produto |
| preco_sugerido_reais | number | Sim | Preço sugerido em reais |
| unidade | string | Sim | Unidade de venda (UN, EMB, etc) |
| descricao_curta | string | Sim | Descrição breve do produto |
| url_imagem_placeholder | string | Sim | URL da imagem do produto |
| categoria | string | Não | Categoria do produto |

---

**💼 Template Profissional**  
Ideal para empresas que precisam de catálogos modernos e responsivos. 