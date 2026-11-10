# Diário de Decisões

Registro das decisões relevantes do projeto, com contexto e justificativa. Cada decisão indica a data, a escolha realizada e as alternativas consideradas. Este documento alimenta as seções de arquitetura, premissas e limitações do README.

A numeração recomeça nesta fase. As decisões das fases anteriores estão nos respectivos repositórios.

---

## D-001 · Contagem por cálculo, texto como evidência

**Data:** 01/11/2026 · **Etapa:** Fundação

**Decisão:** a solução combina duas fontes de verdade. As perguntas de contagem ("principais", "mais frequentes") são respondidas por ferramentas que calculam sobre a base inteira de comentários etiquetados. A busca por sentido (o RAG propriamente dito) recupera os comentários que servem de prova. O modelo de linguagem escolhe a ferramenta, lê o resultado e redige a resposta, mas não produz nenhum número.

**Contexto:** três das cinco perguntas de referência do enunciado pedem frequência ou padrão. Um RAG convencional recupera poucos comentários parecidos com a pergunta, e poucos comentários não informam frequência.

**Justificativa:** um número escrito pelo modelo a partir de cinco exemplos tem aparência de estatística sem ser uma. O enunciado avalia principalmente a coerência entre resposta e evidência, e esse é o modo de falha mais provável de um RAG convencional neste problema.

**Alternativas consideradas:** RAG convencional, com o modelo inferindo frequência a partir dos comentários recuperados (descartado pela falta de sustentação dos números); documentos-resumo pré-calculados e recuperados por similaridade (descartado porque a busca por similaridade sobre resumos continua imprecisa, e cobrir todas as combinações de tema, período, categoria e nota exigiria gerar resumos para cada combinação).

---

## D-002 · Três verificações antes de responder

**Data:** 01/11/2026 · **Etapa:** Fundação

**Decisão:** antes de responder, o sistema verifica, nesta ordem: se a pergunta é do tema da solução; se existe ferramenta capaz de respondê-la; e se há avaliações suficientes sob o recorte pedido. Cada "não" gera uma recusa com mensagem própria. Na recusa por falta de ferramenta, o sistema apresenta a lista do que consegue responder, gerada a partir das próprias ferramentas. Depois da geração, uma última verificação exige que toda afirmação cite ao menos uma avaliação.

**Contexto:** o enunciado pede tratamento para três situações: ausência de avaliações relevantes, evidência insuficiente e pergunta fora do escopo.

**Justificativa:** as três situações têm causas diferentes e pedem respostas diferentes ao usuário. Uma recusa única ("não sei") não diz se o problema é o assunto, a capacidade do sistema ou a falta de dados. Gerar a lista de capacidades a partir das ferramentas evita que ela fique desatualizada quando novas ferramentas forem adicionadas.

**Alternativas consideradas:** recusa única por limiar de similaridade (descartada por não distinguir as causas); deixar o próprio modelo decidir quando recusar, sem verificações explícitas (descartada por não ser verificável nem mensurável).

---

## D-003 · Escopo nas cinco perguntas do enunciado, com filtros abertos

**Data:** 01/11/2026 · **Etapa:** Fundação

**Decisão:** o conjunto de ferramentas cobre as cinco perguntas de referência do enunciado. Dentro de cada ferramenta, os filtros ficam abertos às informações disponíveis na base (período, categoria de produto, faixa de nota, estado). A entrega é tratada como primeiro MVP, e novas perguntas entram depois como novas ferramentas.

**Contexto:** era preciso delimitar o que o sistema responde para que a recusa por falta de ferramenta fosse possível e verificável.

**Justificativa:** travar as perguntas define as ferramentas; travar também os filtros transformaria o sistema numa lista fixa de cinco respostas. "Quais os principais problemas" e "quais os principais problemas em móveis em 2018" são a mesma ferramenta com filtros diferentes.

**Alternativas consideradas:** perguntas totalmente livres (descartada por tornar impossível verificar o que o sistema sabe responder); respostas fixas para as cinco perguntas (descartada por não permitir exploração).

---

## D-004 · Comportamento padrão das ferramentas

**Data:** 01/11/2026 · **Etapa:** Fundação

**Decisão:** quando o usuário não informa a quantidade de itens, a ferramenta usa um valor padrão (todos os temas, ou os 10 primeiros detalhes). Quando pede mais itens do que existem no nível de tema, a ferramenta desce para o nível de detalhe. Os valores padrão ficam no código da ferramenta, e a descrição da ferramenta instrui o modelo a não preencher a quantidade quando o usuário não a informou. Toda resposta começa declarando o recorte usado (quantidade, critério de ordenação e período).

**Contexto:** usuários fazem a mesma pergunta de formas diferentes ("quais os principais atritos?", "top 7 atritos com o cliente"), com ou sem quantidade.

**Justificativa:** sem valor padrão no código, o modelo escolhe uma quantidade por conta própria e a mesma pergunta pode voltar com cortes diferentes. Declarar o recorte torna visível um critério que, de outra forma, ficaria escondido: "principais" pode significar mais frequentes, de pior nota ou mais graves.

**Alternativas consideradas:** deixar o modelo escolher a quantidade (descartada pela falta de controle e de repetibilidade); quantidade fixa em todos os níveis (descartada porque, com poucos temas, um corte esconde parte do quadro).

---

## D-005 · Cada pergunta é independente

**Data:** 01/11/2026 · **Etapa:** Fundação

**Decisão:** o sistema não guarda memória entre perguntas. Uma pergunta de acompanhamento como "e em 2018?" não é resolvida a partir da pergunta anterior.

**Justificativa:** memória de conversa exige uma peça adicional para interpretar referências à pergunta anterior. Fica como evolução do MVP, dado o prazo.

---

## D-006 · Peças técnicas das aulas da fase

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** a solução usa as mesmas peças das aulas de LangChain e IA Generativa: modelos do Google (Gemini) ou da OpenAI, escolhidos por variável de ambiente; resposta estruturada com Pydantic; ferramentas declaradas com `@tool`; busca vetorial com FAISS; fluxo montado com LangGraph. O ambiente usa Python 3.12, a versão do material do curso.

**Contexto:** o material de referência da coordenação do curso mostra quais bibliotecas e padrões foram usados nas aulas.

**Justificativa:** reaproveitar as peças evita reinventar o que já foi ensinado e permite relacionar cada parte da solução a uma aula. O que o projeto cria é o que é específico do caso: a preparação dos dados, os temas, o cálculo das ferramentas e as verificações do fluxo.

**Alternativas consideradas:** busca vetorial com Chroma e modelo da Anthropic, propostos no primeiro esboço (descartados para alinhar ao material do curso).

---

## D-007 · Embedding do Google, como na aula 3 de LangChain

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** a transformação dos comentários em vetores para a busca por sentido usa o modelo de embedding do Google pelo LangChain, com índice FAISS, no mesmo padrão da aula 3.

**Justificativa:** o projeto já depende da chave do Google para gerar respostas, então o embedding pelo mesmo provedor não acrescenta dependência. Segue o padrão do curso.

**Alternativas consideradas:** modelo de embedding executado localmente, sem chave (descartado: o ganho de reconstruir o índice sem chave é pequeno, já que a geração de respostas exige chave de qualquer forma).

---

## D-008 · Etiquetagem pelo modelo de linguagem, medida contra amostra manual

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** nesta entrega, o modelo de linguagem etiqueta todos os comentários uma única vez, na preparação da base, com resposta estruturada. Uma amostra de cerca de 150 comentários é etiquetada à mão e usada para medir o acerto do modelo. O treino de um classificador próprio fica registrado como próximo passo.

**Contexto:** as ferramentas de contagem dependem de cada comentário ter etiquetas de tema. O primeiro esboço previa treinar um classificador (TF-IDF com Regressão Logística) a partir de uma amostra etiquetada pelo modelo, para que avaliações novas pudessem ser etiquetadas sem chamada de API.

**Justificativa:** com cerca de 40 mil comentários, etiquetar tudo com o modelo é viável em custo e tempo, e evita criar e manter um segundo modelo. O classificador próprio só se paga com volume recorrente de avaliações novas, o que está fora do escopo do MVP. A amostra manual é o que permite confiar nas contagens.

**Alternativas consideradas:** classificador próprio treinado com as etiquetas do modelo (adiado para evolução); usar a nota da avaliação como sentimento (descartado, ver D-009).

---

## D-009 · Etiqueta por tema, sentido e detalhe, extraída do texto

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** cada comentário recebe zero, uma ou várias etiquetas, cada uma composta por tema (ex.: entrega), sentido (positivo ou negativo) e detalhe (ex.: atraso). A nota da avaliação não é usada como sentimento: fica como informação complementar.

**Contexto:** o enunciado pergunta tanto por problemas quanto por elogios, e um mesmo comentário frequentemente trata de mais de um assunto ("produto ótimo, mas a entrega atrasou").

**Justificativa:** etiquetar só problemas deixaria sem resposta a pergunta sobre elogios. A nota é dada ao pedido, não ao comentário, e não distingue assuntos. Como um comentário pode ter mais de um tema, os percentuais por tema não somam 100% e são apresentados como parcela de comentários que mencionam o tema.

**Alternativas consideradas:** um único tema por comentário (descartado por perder comentários com mais de um assunto); sentimento derivado da nota (descartado pelos motivos acima).

---

## D-010 · Ambiente e obtenção dos dados

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** o ambiente virtual usa Python 3.12, instalado com a ferramenta `uv`. A base da Olist é baixada do Kaggle pelo endereço público da API, sem login, e fica fora do controle de versão.

**Contexto:** a máquina de desenvolvimento tem apenas Python 3.14, e o instalador do Windows estava bloqueado por instalações pendentes do sistema. Algumas bibliotecas do projeto ainda não têm suporte ao 3.14.

**Justificativa:** o `uv` baixa uma versão portátil do Python sem passar pelo instalador do Windows. O download sem login torna a obtenção dos dados reproduzível por qualquer pessoa, com um comando documentado no README.

---

## D-011 · Lista de temas proposta pelo modelo de linguagem, com duas amostras

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** a lista de temas e detalhes é proposta pelo modelo de linguagem a partir de duas amostras independentes de cerca de 1.000 comentários cada, sorteadas em proporção por nota (composição revista em D-014). Além da lista, o modelo devolve, para cada etiqueta, definição, critérios de inclusão e exclusão e exemplos reais identificados pelo código da avaliação. As duas propostas são comparadas e a versão final é revisada à mão.

**Contexto:** o primeiro esboço previa descobrir os temas com TF-IDF e NMF (aula 6 de NLP). O NMF agrupa por palavras que aparecem juntas, não por sentido, e tende a gerar grupos redundantes: clientes descrevem o mesmo atraso com vocabulários diferentes ("prazo", "ainda não recebi", "não chegou"), e cada vocabulário pode virar um grupo. Também pode juntar sentidos opostos que compartilham palavras ("chegou rápido" e "chegou quebrado").

**Justificativa:** o modelo de linguagem agrupa por sentido e já entrega o rascunho do manual de etiquetagem, com critérios. A comparação entre duas amostras mede a estabilidade da lista: temas presentes nas duas são confiáveis; divergências indicam amostra insuficiente. Os exemplos com código da avaliação permitem conferir que nenhum exemplo foi inventado. O volume (duas chamadas, cerca de 25 mil tokens cada) cabe no plano gratuito.

**Alternativas consideradas:** TF-IDF e NMF com curadoria manual (descartado pela redundância e pelo volume de leitura; pode ser usado ao final apenas para conferir se algum assunto frequente ficou de fora); lista definida a partir das etapas da jornada de compra, sem consulta aos dados (descartada pelo risco de deixar de fora assuntos que os clientes de fato relatam).

---

## D-012 · Manual de etiquetagem e piloto antes do gabarito

**Data:** 08/11/2026 · **Etapa:** Fundação

**Decisão:** antes de qualquer etiquetagem, cada etiqueta é descrita num manual com definição, o que entra, o que não entra, regra de desempate e exemplos. Os três campos (tema, sentido e detalhe) são fechados, com a opção "outro". Quando o comentário tem elogio e crítica, as duas etiquetas são registradas. O gabarito de 150 comentários é precedido de um piloto de 20, cujas dúvidas são usadas para ajustar o manual. O mesmo manual serve de instrução ao modelo de linguagem.

**Contexto:** o gabarito manual mede o acerto do modelo. Se a definição das etiquetas for ambígua, a etiquetagem manual carrega dúvida, e a comparação passa a medir a ambiguidade da regra em vez do erro do modelo. Uma verificação preliminar mostrou que cerca de 1 em cada 10 comentários tem conectivo de contraste ("mas", "porém", "só que"), proporção que chega a 27% nas avaliações de nota 3 e cai para 4% nas de nota 5.

**Justificativa:** com o mesmo manual para os dois lados, uma divergência entre a etiquetagem manual e a do modelo aponta erro de um deles, e não regra mal escrita. O piloto revela as dúvidas num momento em que ainda é possível corrigir a regra sem refazer o gabarito. A opção "outro" evita forçar comentários em valores errados e sinaliza itens ausentes na lista.

**Alternativas consideradas:** etiquetar o gabarito apenas com a lista de nomes, sem critérios (descartada pela incerteza que introduz na medição); campos livres (descartada porque formas diferentes de descrever a mesma coisa seriam contadas como itens diferentes).

---

## D-013 · Percentuais sempre sobre os comentários, nunca sobre os clientes

**Data:** 08/11/2026 · **Etapa:** Análise exploratória

**Decisão:** toda resposta que apresenta percentual informa que a base são os comentários ("X% dos comentários mencionam atraso"), e nunca o generaliza para os clientes ou pedidos.

**Contexto:** a análise exploratória mostrou que 76,5% das avaliações de nota 1 têm comentário escrito, contra 35,8% das de nota 5. Com isso, a nota 1 representa 11,5% das avaliações, mas 21,4% dos comentários.

**Justificativa:** os comentários dão quase o dobro do peso à insatisfação forte. Um percentual calculado sobre eles descreve quem escreveu, e não o conjunto dos clientes.

---

## D-014 · Amostra para a lista de temas com peso maior nos comentários negativos

**Data:** 08/11/2026 · **Etapa:** Análise exploratória

**Decisão:** cada uma das duas amostras de 1.000 comentários usadas na construção da lista de temas (D-011) é composta por 60% de notas 1 e 2, 15% de nota 3 e 25% de notas 4 e 5. Comentários idênticos depois da padronização (minúsculas, sem acento, sem pontuação) entram uma única vez. Esta decisão substitui a amostragem em proporção às notas prevista em D-011.

**Contexto:** testou-se a hipótese de que clientes insatisfeitos descrevem o motivo com mais detalhe, e satisfeitos usam frases genéricas. A repetição de frases idênticas é de 27,6% na nota 5 contra 9,7% na nota 1, e as mais repetidas são elogios genéricos ("muito bom", 598 vezes; "ótimo", 471). Referências a número, troca, pagamento e características do produto aparecem quase só nas notas baixas; os elogios, quando têm conteúdo, concentram-se no prazo de entrega. A nota 3 é a que mais combina elogio e crítica (26,7% dos comentários com conectivo de contraste).

**Justificativa:** a amostra serve para descobrir quais assuntos existem, e os comentários negativos trazem a maior variedade. Uma amostra em proporção às notas teria metade das vagas em elogios de pouca variação. Os 25% de notas 4 e 5 são suficientes para cobrir os poucos temas de elogio, exigidos pela pergunta do enunciado sobre o que os clientes mais elogiam. Remover cópias idênticas evita gastar vagas com a mesma frase; a frequência de cada comentário continua disponível para as contagens.

**Alternativas consideradas:** amostra em proporção às notas (descartada pelo motivo acima); amostra só com comentários negativos (descartada por deixar sem temas a pergunta sobre elogios); amostra equilibrada, 20% por nota (descartada por não refletir a diferença de variedade observada).

**Limitação registrada:** as medidas de repetição e de referência concreta são aproximadas (cópia exata e lista de palavras). Os desvios conhecidos de ambas reduzem a diferença entre notas baixas e altas, de modo que a diferença real tende a ser maior que a observada.

---

## D-015 · Etiqueta para elogio sem assunto

**Data:** 08/11/2026 · **Etapa:** Análise exploratória

**Decisão:** a lista de temas inclui a etiqueta "elogio geral, sem assunto", com sentido positivo, para comentários que elogiam sem citar nenhum aspecto da compra ("muito bom", "recomendo", "nota 10").

**Justificativa:** esses comentários são frequentes nas notas altas. Sem uma etiqueta própria, ou ficariam fora das contagens ou seriam forçados num tema que não citam, distorcendo a frequência daquele tema.

---

## D-016 · Um documento por avaliação, não por linha da tabela

**Data:** 08/11/2026 · **Etapa:** Análise exploratória

**Decisão:** a base de conhecimento tem um documento por código de avaliação (`review_id`). Avaliações replicadas em mais de um pedido entram uma única vez.

**Contexto:** a tabela de avaliações tem 99.224 linhas e 98.410 códigos de avaliação distintos. Em 1.603 linhas (1,6%), a mesma avaliação, com texto e data idênticos, aparece ligada a pedidos diferentes, o que indica uma pesquisa respondida uma vez e replicada para os pedidos de uma mesma compra. Entre as linhas com comentário, 608 estão nessa situação.

**Justificativa:** manter as linhas replicadas faria o mesmo comentário ser contado mais de uma vez nas ferramentas de contagem e aparecer repetido como evidência.

**Pendência registrada:** como uma avaliação pode estar ligada a mais de um pedido, com produtos e prazos possivelmente diferentes, a forma de associar categoria e prazo de entrega a ela é decidida na etapa de enriquecimento.

---

## D-017 · Todas as tabelas da base entram, resumidas por pedido, com distância entre vendedor e cliente

**Data:** 08/11/2026 · **Etapa:** Enriquecimento

**Decisão:** a tabela base mantém uma linha por avaliação e recebe informações de todas as tabelas da Olist, resumidas por pedido: datas e status do pedido, estado e cidade do cliente, categorias dos produtos, número de itens, valores de produto e frete, forma de pagamento e parcelas, código e estado do vendedor. A tabela de geolocalização entra como a distância, em quilômetros, entre o CEP do vendedor e o CEP do cliente, e como a localização aproximada do cliente.

**Contexto:** as cinco perguntas do enunciado não dependem de pagamentos, vendedores nem geolocalização. A ausência de pergunta hoje, porém, não torna essas informações dispensáveis: elas sustentam ferramentas futuras ("quais vendedores concentram reclamações?", "reclamações de atraso são mais comuns em entregas longas?").

**Justificativa:** resumir por pedido preserva o grão de uma linha por avaliação. A distância entre vendedor e cliente permite relacionar atraso e reclamação à extensão do trajeto. No modelo da Olist, o produto é enviado pelo próprio vendedor, então o CEP do vendedor é a melhor aproximação disponível da origem.

**Limitação registrada:** a base não informa a localização de centros de distribuição nem se algum vendedor despachava a partir de outro endereço, como um armazém terceirizado. A distância calculada é a do endereço do vendedor ao do cliente, e não a do trajeto real do produto.

**Evolução proposta:** com a localização dos centros de distribuição, seria possível identificar as faixas de distância mais afetadas por atraso e as regiões sem cobertura de um centro próximo, oferecendo base para decisões de operação logística, como onde instalar ou reforçar centros de distribuição.

---

## D-018 · Regras de junção para pedidos com vários produtos, avaliações em vários pedidos e pedidos não entregues

**Data:** 08/11/2026 · **Etapa:** Enriquecimento

**Decisão:**

1. Um pedido com produtos de categorias diferentes recebe todas as suas categorias. O filtro por categoria encontra o comentário se qualquer produto do pedido for daquela categoria.
2. Uma avaliação ligada a mais de um pedido (D-016) recebe as categorias de todos os pedidos e o maior atraso entre eles.
3. Um pedido sem data de entrega recebe a faixa "não entregue", em vez de atraso vazio.

**Justificativa:** escolher uma única categoria por pedido descartaria parte dos produtos comprados, sem critério que diga qual deles motivou o comentário. O maior atraso é usado porque a experiência mais negativa da compra tende a ser a que motiva a avaliação. A faixa "não entregue" preserva a situação mais grave da jornada: "não recebi o produto" é a reclamação mais repetida da base.

**Alternativas consideradas:** categoria do produto de maior valor (descartada por supor, sem evidência, que o item mais caro motivou o comentário); atraso médio entre os pedidos (descartado por diluir a experiência negativa).

---

## D-019 · Regras de resumo por pedido

**Data:** 08/11/2026 · **Etapa:** Enriquecimento

**Decisão:**

| Situação | Regra |
|---|---|
| pedido com vários vendedores (1,3% dos pedidos) | lista dos vendedores; distância e atraso no despacho pelo pior caso |
| pedido com vários pagamentos (3,0%) | forma principal é a de maior valor; valor pago é a soma; parcelas é o máximo |
| prefixo de CEP com vários pontos de geolocalização (94,5% dos prefixos) | mediana da latitude e da longitude |
| pedido sem item (775) ou produto sem categoria (610) | categoria "sem informação" |
| CEP sem localização (278 de clientes, 7 de vendedores) | distância vazia |

**Contexto:** a verificação das ligações entre as tabelas confirmou junção direta entre pedido e cliente, item e produto, item e vendedor, e mostrou ligações de um para vários em itens, pagamentos e geolocalização, que precisam ser resumidas para manter uma linha por avaliação.

**Justificativa:** o pior caso entre vendedores segue a lógica de D-018, em que a experiência mais negativa tende a motivar a avaliação. A forma de pagamento de maior valor representa como o pedido foi efetivamente pago, já que os pagamentos múltiplos costumam combinar um meio principal com vouchers. A mediana das coordenadas não é deslocada por pontos registrados fora da área do CEP, que existem na tabela de geolocalização.
