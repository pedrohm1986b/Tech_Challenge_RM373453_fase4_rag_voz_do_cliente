# Escopo do projeto

Voice of Customer Intelligence com RAG sobre as avaliações de clientes da base Brazilian E-Commerce Public Dataset by Olist.

| | |
|---|---|
| Aluno | Pedro Henrique Martinez Bertolo, RM373453 |
| Fase | 4, Deep Learning e NLP |
| Prazo | 17/11/2026 |
| Modalidade | individual |
| Documento | iniciado em 01/11/2026, revisado em 08/11/2026 |

Este documento fixa o que a solução é, o que ela não é e as premissas que sustentam as escolhas técnicas. As decisões, com contexto e alternativas, estão no [diário de decisões](decisoes.md).

---

## 1. O problema

Uma empresa de e-commerce acumula milhares de avaliações escritas. A nota de 1 a 5 mostra o nível de satisfação, mas não diz o motivo. O motivo está no texto, e ler o texto à mão não escala.

A solução deve permitir que gestores e analistas perguntem em linguagem natural e recebam respostas fundamentadas nos comentários reais, com as evidências à vista.

Perguntas de referência do enunciado:

1. Quais são os principais problemas relatados pelos clientes?
2. Quais reclamações relacionadas à entrega aparecem com maior frequência?
3. O que os clientes mais elogiam em suas experiências de compra?
4. Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?
5. Quais avaliações sustentam a conclusão de que existem problemas recorrentes de prazo?

## 2. O que o enunciado fixa e o que deixa em aberto

| Fixado pelo enunciado | A cargo do projeto |
|---|---|
| Arquitetura baseada em RAG | modelo de embedding |
| Base de conhecimento com seleção justificada | banco vetorial |
| Resposta fundamentada em evidência recuperada | estratégia de recuperação |
| Tratamento de pergunta sem evidência suficiente | modelo de linguagem |
| Rastreabilidade do insight até a avaliação | organização dos documentos |
| Repositório público e vídeo de até 7 minutos | uso de metadados (opcional) |

## 3. A questão central do desafio

Das cinco perguntas de referência, **três são perguntas de contagem**: "principais", "maior frequência", "padrões recorrentes".

Um RAG convencional busca os poucos comentários mais parecidos com a pergunta e os entrega ao modelo de linguagem. Para "quais reclamações de entrega aparecem com maior frequência", ele traz cinco comentários sobre entrega. Cinco comentários não informam frequência. O modelo então escreve uma resposta convincente e sem sustentação nos dados.

O enunciado avisa que "não serão avaliadas apenas respostas bem escritas", e sim a capacidade de "gerar respostas coerentes com as evidências encontradas". A arquitetura deste projeto responde a essa questão separando duas fontes de verdade: **a contagem vem de cálculo sobre a base inteira, e o texto recuperado vem como prova**.

## 4. Premissas

### P1. A nota da avaliação não é o sentimento do comentário

A nota é dada ao **pedido**, não ao comentário. Ela mistura produto, entrega, vendedor e expectativa num número só, e não distingue assuntos: um cliente pode elogiar o produto e reclamar da entrega na mesma frase. Por isso o assunto e o sentido são extraídos do texto. A nota fica na base como informação complementar, e a divergência entre nota e texto vira objeto de análise.

### P2. As etiquetas são produzidas uma vez, na preparação

Cada comentário recebe suas etiquetas de assunto uma única vez, na preparação da base, e o resultado é salvo. Nenhuma pergunta do usuário provoca nova etiquetagem. Nesta entrega, quem etiqueta é o modelo de linguagem, com resposta em formato estruturado, e a qualidade é medida contra uma amostra etiquetada à mão. O modelo e a etiquetagem manual seguem o mesmo manual de etiquetagem (seção 6), para que uma divergência indique erro de etiquetagem, e não ambiguidade da regra. Para escalar com avaliações novas, a evolução prevista é treinar um classificador próprio com essas etiquetas (ver seção 7).

### P3. O comentário é a unidade de busca

Cada avaliação com texto é um documento da base, sem divisão em pedaços. A divisão em pedaços (*chunking*) existe para quebrar documentos longos; um comentário de e-commerce tem uma ou duas frases e já é a menor unidade com sentido. A distribuição de tamanho dos comentários, medida na análise exploratória, sustenta essa escolha.

### P4. Nenhum número é produzido pelo modelo de linguagem

Toda contagem, percentual e ranking da resposta vem de cálculo em código sobre a base etiquetada. O modelo de linguagem escolhe qual ferramenta usar e com quais filtros; a ferramenta calcula; o modelo redige a resposta a partir do resultado.

| Ferramenta | Responde |
|---|---|
| `ranking_temas` | quais são os principais problemas ou elogios |
| `detalhar_tema` | quais problemas dentro de um tema (ex.: dentro de entrega) |
| `serie_temporal` | como um tema evolui ao longo do tempo |
| `buscar_comentarios` | quais comentários tratam de um assunto (a busca por sentido, o RAG) |
| `divergencia_nota_texto` | quais avaliações têm nota que contradiz o texto |
| `cobertura` | quantas avaliações existem sob um filtro |

> **Atualização (D-029):** na implementação, as seis ferramentas viraram duas. `consultar_base` recebe um formulário com campos fechados (medida, agrupamento, filtros, segundo grupo para comparação) e cobre o ranking, o detalhe de um tema, a série no tempo, os padrões e a cobertura; `buscar_comentarios` é a busca por sentido. A divergência entre nota e texto ficou fora do MVP. A verificação de dados suficientes passou a ter três faixas: nenhum comentário (recusa), de 1 a 29 (amostra pequena, sem percentual, com aviso) e 30 ou mais (resposta completa).

Regras de comportamento das ferramentas:

- **Toda resposta de contagem também busca comentários**, para citar as avaliações que sustentam o número. Número sem evidência não sai.
- **Quantidade padrão.** Quando o usuário não diz quantos itens quer ("quais os principais atritos?"), a ferramenta usa um valor padrão: todos os temas, ou os 10 primeiros detalhes. O modelo de linguagem é instruído a não inventar uma quantidade.
- **Nível de detalhe.** Se o usuário pede mais itens do que existem no nível de tema ("top 7 atritos" com 5 temas), a ferramenta desce para o nível de detalhe, onde há mais itens.
- **Recorte declarado.** Toda resposta começa dizendo o que considerou, por exemplo: "os 5 temas de insatisfação, ordenados por volume, em toda a base (2016 a 2018)".
- **Percentuais sobre os comentários.** Quem dá nota baixa comenta duas vezes mais que quem dá nota alta, então os percentuais descrevem os comentários, não os clientes, e a resposta diz isso (D-013).
- **Filtros são opcionais.** Período, categoria de produto, faixa de nota e estado podem ser aplicados; sem filtro, vale a base inteira, e a resposta diz isso.

### P5. Ausência de evidência é uma resposta válida

Antes de responder, o sistema passa por três verificações, e cada recusa tem uma mensagem diferente:

| Verificação | Exemplo de pergunta recusada | Resposta do sistema |
|---|---|---|
| A pergunta é do tema? | "qual a cotação do dólar?" | o assunto não faz parte do que o sistema trata |
| Existe ferramenta para ela? | "qual vendedor tem mais reclamações?" | ainda não consegue responder, e mostra a lista do que consegue |
| Há dados suficientes? | "o que reclamam da entrega em Roraima em 2016?" | existem poucas avaliações, insuficientes para concluir |

Depois de gerada, a resposta passa por uma última verificação: toda afirmação precisa citar ao menos uma avaliação da base. A lista do que o sistema consegue responder é gerada a partir das próprias ferramentas, para continuar correta quando novas ferramentas forem adicionadas.

### P6. Reaproveitar as peças do curso e criar só o que é do caso

As peças técnicas seguem as aulas da fase: modelo de linguagem, resposta estruturada, ferramentas, busca vetorial e fluxo em grafo vêm do material de LangChain e IA Generativa. O que o projeto cria é o que nenhuma aula tem: a preparação dos dados da Olist, os temas de reclamação e elogio, o cálculo dentro das ferramentas e as verificações do fluxo.

### P7. Comentário de cliente é conteúdo não confiável

O texto recuperado entra no prompt como dado, nunca como instrução, delimitado de forma explícita. Um comentário que contenha algo como "ignore as instruções anteriores" é tratado como texto comum. É a injeção indireta de prompt, risco destacado na aula de ética e segurança.

## 5. Arquitetura

```
PREPARAÇÃO (roda uma vez)

  9 arquivos CSV da Olist
     |
     +-- seleção ............. avaliações com comentário escrito
     +-- enriquecimento ...... nota, data, categoria do produto, atraso da entrega, estado
     +-- lista de temas ...... modelo de linguagem propõe temas e critérios
     |                         a partir de duas amostras; revisão humana
     +-- manual .............. definição, o que entra, o que não entra, exemplos
     +-- etiquetagem ......... modelo de linguagem etiqueta cada comentário
     |                         amostra etiquetada à mão mede o acerto
     |
     +--> TABELA ETIQUETADA    uma linha por comentário e tema, com as informações do pedido
     +--> ÍNDICE FAISS          um comentário = um documento, para a busca por sentido


CONSULTA (a cada pergunta)

  pergunta
     |
  [é do tema?] ............... não -> recusa: fora do tema
     |
  [existe ferramenta?] ....... não -> recusa: ainda não responde + lista do que responde
     |
  ferramentas de contagem (tabela etiquetada) + busca de comentários (índice FAISS)
     |
  [há dados suficientes?] .... não -> recusa: evidência insuficiente
     |
  resposta com recorte declarado e comentários citados
     |
  [toda afirmação cita avaliação?] .. não -> recusa
     |
  resposta final
```

## 6. Etiquetas

Cada comentário pode receber **várias etiquetas**, ou nenhuma (classificação multirrótulo). Cada etiqueta tem três partes:

| Comentário | Tema | Sentido | Detalhe |
|---|---|---|---|
| "chegou 15 dias atrasado" | entrega | negativo | atraso |
| "chegou antes do prazo" | entrega | positivo | rapidez |
| "tecido de ótima qualidade" | produto | positivo | qualidade |

Os temas e detalhes acima são ilustrativos. Como um comentário pode estar em mais de um tema, os percentuais por tema não somam 100%: a resposta informa a parcela de comentários que **mencionam** cada tema.

**Como a lista é construída (etapa 3).** O modelo de linguagem lê duas amostras independentes de cerca de 1.000 comentários e propõe temas, detalhes e critérios. Cada amostra tem 60% de notas 1 e 2, 15% de nota 3 e 25% de notas 4 e 5, sem cópias idênticas, porque os comentários negativos trazem a maior variedade de assuntos e os elogios se concentram em poucos temas (D-014). A lista inclui a etiqueta "elogio geral, sem assunto" para elogios que não citam nenhum aspecto da compra (D-015); na etiquetagem da base, ela passou a se chamar "geral, sem assunto" e a aceitar também a reclamação genérica (D-026). As duas propostas são comparadas: temas que aparecem nas duas são estáveis; divergências indicam amostra insuficiente. A proposta é revisada à mão (juntar redundâncias, separar misturas, decidir casos difíceis).

**Campos fechados.** Tema, sentido e detalhe só aceitam valores da lista. Cada lista tem a opção "outro", para que nenhum comentário seja forçado num valor errado; uma proporção alta de "outro" indica item faltando na lista.

**Manual de etiquetagem.** Cada etiqueta tem definição, o que entra, o que não entra, regra de desempate e exemplos reais com o código da avaliação. O mesmo manual orienta a etiquetagem manual e serve de instrução ao modelo de linguagem. Regra geral: quando o comentário tem elogio e crítica, as duas etiquetas são registradas. Cerca de 1 em cada 10 comentários tem conectivo de contraste ("mas", "porém"), chegando a 27% nas avaliações de nota 3.

**Piloto.** Antes dos 150 comentários do gabarito, um piloto com 20 comentários registra as dúvidas da etiquetagem manual, e o manual é ajustado. A lista é fechada antes da etiquetagem do gabarito.

## 7. Dentro e fora do escopo

| Dentro | Fora |
|---|---|
| Avaliações com comentário escrito (40.518 avaliações distintas, de 99.224 linhas) | avaliações sem texto (entram só nas contagens de total) |
| Tema, sentido e detalhe extraídos do texto | previsão de nota ou de cancelamento |
| Informações do pedido como filtro (desafio adicional) | recomendação de produto |
| Ferramentas de contagem e busca de comentários | consulta livre ao banco gerada pelo modelo (texto para SQL) |
| Três verificações de recusa e verificação de citação | memória de conversa (cada pergunta é independente) |
| Interface de demonstração | autenticação, multiusuário, publicação em nuvem |
| Conjunto de avaliação com métricas | classificador próprio treinado (próximo passo) |

A memória de conversa e o classificador próprio ficam como evolução natural deste MVP. Outra evolução depende de dado externo: com a localização dos centros de distribuição, seria possível identificar as faixas de distância mais afetadas por atraso e as regiões sem cobertura de um centro próximo, apoiando decisões de operação logística (D-017). A lista de ferramentas também: novas perguntas entram como novas ferramentas.

## 8. Entregáveis

| Entregável | Conteúdo |
|---|---|
| Repositório público no GitHub | código, instruções de instalação e execução, README |
| README | arquitetura, tecnologias, estratégia do RAG, preparação da base, justificativa das decisões, exemplos de pergunta e resposta, reprodução |
| Vídeo de até 7 minutos | problema, arquitetura, estratégia, recuperação, demonstração, evidências, decisões técnicas |
| Arquivo de entrega | no padrão das fases anteriores, com o link do repositório e do vídeo |

## 9. Etapas

| # | Etapa | Entrega | Peso | Data prevista |
|---|---|---|---|---|
| 0 | Fundação | repositório, ambiente, dados, escopo e diário de decisões | 5% | 08/11 |
| 1 | Análise exploratória | cobertura de texto, tamanho dos comentários, notas, série temporal | 10% | 09/11 |
| 2 | Enriquecimento | junção com pedidos, produtos e clientes; atraso de entrega | 5% | 09/11 |
| 3 | Lista de temas e manual | proposta do modelo em duas amostras, revisão, manual de etiquetagem | 10% | 10/11 |
| 4 | Etiquetagem | piloto de 20, gabarito de 150, etiquetagem completa pelo modelo, medida de acerto | 15% | 11/11 |
| 5 | Base de busca | índice FAISS com embedding do Google | 10% | 12/11 |
| 6 | Ferramentas e fluxo | as seis ferramentas, as verificações, o grafo do LangGraph | 20% | 13 e 14/11 |
| 7 | Avaliação | perguntas de teste, acerto de ferramenta, qualidade da busca, recusas | 10% | 15/11 |
| 8 | Interface | aplicação de consulta com os comentários citados | 5% | 15/11 |
| 9 | Documentação e vídeo | README completo, apresentação, roteiro e gravação | 10% | 16/11 |

O dia 17 fica de margem. Cada etapa é desenvolvida em notebook com prefixo `desenv_`, célula a célula, e promovida a script com prefixo `prod_` quando aprovada.

## 10. Riscos

| Risco | Como tratar |
|---|---|
| Limite diário do plano gratuito do Gemini na etiquetagem | enviar vários comentários por chamada; se faltar, concluir no dia seguinte ou usar a OpenAI |
| Etiquetas do modelo com baixo acerto | revisar a instrução de etiquetagem contra a amostra manual e reetiquetar |
| Lista de temas instável entre amostras | comparar as propostas das duas amostras; se divergirem muito, ampliar a amostra |
| Dúvida na etiquetagem manual | piloto de 20 comentários antes do gabarito, com ajuste do manual |
| Plano gratuito do Gemini usa o conteúdo enviado para melhorar produtos do Google | aceitável aqui por a base ser pública e anonimizada; com dados reais de clientes, usar plano pago |
| O modelo escolhe a ferramenta errada | regras de preenchimento na descrição de cada ferramenta; o teste mede acerto de ferramenta separadamente |
| Pergunta fora do que as ferramentas cobrem | comportamento esperado: recusa com a lista do que o sistema responde |
| Prazo de 9 dias em projeto individual | a interface pode ser substituída por um notebook de demonstração |
