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

---

## D-020 · Manual de etiquetagem, versão 1

**Data:** 10/11/2026 · **Etapa:** Lista de temas

**Decisão:** o manual tem cinco temas e treze detalhes, mais a opção "outro" em cada tema:

| Tema | Detalhes |
|---|---|
| entrega | prazo, não recebido, itens faltando, avaria no transporte, retirada na agência |
| produto | conformidade com o anúncio, qualidade |
| preço | preço do produto, frete |
| atendimento | contato e resposta; cancelamento, troca e reembolso; nota fiscal |
| elogio geral | sem assunto |

Produto quebrado: "chegou quebrado" ou "veio danificado" é entrega · avaria no transporte; "parou de funcionar" ou "defeito depois de usar" é produto · qualidade. O manual fica em `reports/lista_temas/manual_v1.json`.

**Contexto:** as quatro propostas do modelo (duas amostras, com e sem exemplos de tema nas regras) concordaram em quatro temas: entrega, produto, atendimento e elogio geral. O teste sem exemplos, feito para verificar se os exemplos tinham ancorado o modelo, não trouxe tema novo. A busca por palavras na base inteira encontrou assuntos pequenos ausentes das propostas: preço e frete (3,2% dos comentários), cancelamento (1,3%), nota fiscal (1,1%) e a retirada do produto nos Correios por quem pagou o frete. Relatos sobre o site ou o aplicativo não apareceram: as menções ao site são elogios.

**Justificativa:** os temas estáveis entre as propostas formam a estrutura do manual; os detalhes que divergiram entre as propostas foram decididos na revisão, priorizando reclamações frequentes ("não recebido" é a mais repetida da base). O valor do frete ficou em preço, por ser reclamação de custo; a retirada na agência ficou em entrega, porque aparece também em comentários que não citam o frete. As sugestões do modelo de escolher um único tema em comentários com dois assuntos foram descartadas, em favor de D-012.

**Alternativas consideradas:** frete como tema próprio, com os detalhes valor e retirada na agência (descartada porque a retirada na agência aparece sem menção ao frete e ficaria fora do tema); usar apenas os temas propostos pelo modelo (descartada pelos assuntos encontrados na busca).

---

## D-021 · Etiquetagem às cegas da mesma amostra, com racional do modelo

**Data:** 10/11/2026 · **Etapa:** Etiquetagem

**Decisão:** a etiquetagem manual e a do modelo usam os mesmos 170 comentários e o mesmo manual, sem a nota da avaliação. Os comentários das amostras lidas pelo modelo na construção do manual ficam de fora. O modelo registra, para cada etiqueta, o trecho exato do comentário que a motiva e uma justificativa, antes da etiqueta. O resultado do modelo não é consultado antes do fim da etiquetagem manual. A planilha manual tem menus encadeados (sentido, tema, detalhe), aceita várias etiquetas por comentário e a marcação "sem etiqueta".

**Justificativa:** a nota poderia induzir o sentido. Comentários já lidos pelo modelo comprometeriam a independência do gabarito. O trecho e a justificativa permitem avaliar se o raciocínio do modelo coincide com o da etiquetagem manual, e não apenas a etiqueta, e permitem conferir que o trecho existe no comentário. A divisão prévia do comentário em pedaços de sentido único foi considerada e descartada: o trecho citado em cada etiqueta cumpre esse papel sem os erros de um corte por regra (por exemplo, no "mas").

---

## D-022 · Medida de acordo entre etiquetagens

**Data:** 10/11/2026 · **Etapa:** Etiquetagem

**Decisão:** cada etiqueta vale 1, e cada campo que coincide vale um terço: sentido, tema e detalhe. O detalhe só conta quando o tema também coincide. Exemplo: entrega · prazo · negativo contra entrega · não recebido · negativo vale 1/3 + 1/3 = 0,67. A nota do comentário é a do par de etiquetas, uma manual e uma do modelo, que mais pontua; a média dessas notas é a medida principal. Quando as duas etiquetagens marcam "sem etiqueta", a nota é 1; quando só uma marca, é 0. Complementam a medida principal: a cobertura dos assuntos (todas as etiquetas pareadas sem considerar a ordem, com nota zero para etiqueta sem par), o acerto por campo e a proporção de comentários com ao menos uma etiqueta idêntica.

**Justificativa:** errar o sentido ou o tema muda a leitura do comentário; o crédito parcial evita tratar como erro total um comentário em que só o detalhe diverge, muitas vezes por interpretação entre detalhes vizinhos (prazo e não recebido, por exemplo). Usar a etiqueta que melhor coincide aceita interpretações diferentes sobre os assuntos secundários de um comentário com várias etiquetas. Essa escolha é generosa com etiquetas a mais, que inflam as contagens das ferramentas, e por isso a cobertura dos assuntos acompanha a medida principal. A ordem das etiquetas nunca é considerada.

---

## D-023 · Gemini 3.5 Flash-Lite para etiquetar a base inteira

**Data:** 11/11/2026 · **Etapa:** Etiquetagem

**Decisão:** a etiquetagem dos 40.518 comentários usa o `gemini-3.5-flash-lite`, sem o trecho e a justificativa, que ficam restritos à comparação na amostra.

**Contexto:** três modelos etiquetaram os mesmos 170 comentários, com o mesmo manual, a mesma instrução e os mesmos lotes, e foram medidos contra a etiquetagem manual. O `gemini-3.5-flash-lite` teve F1 de 0,771 por etiqueta completa (recall 0,768, precisão 0,775), contra 0,748 do `gemini-3.1-flash-lite` (recall 0,732, precisão 0,766). O ganho se concentra na principal confusão do modelo anterior: o recall de "entrega · não recebido" passou de 0,46 para 0,68. O `gemini-3.8-flash` não concluiu a amostra em 20 minutos; num teste com 5 comentários, levou 2 minutos e 21 segundos, sem tokens de raciocínio, o que projeta cerca de 3 dias para a base inteira.

**Justificativa:** o 3.5 Flash-Lite reduz justamente a confusão entre não recebido e prazo, que distorce as contagens de problemas de entrega. O custo projetado para a base inteira, sem o racional, fica na ordem de poucos dólares, e o tempo, abaixo de uma hora e meia com chamadas em paralelo. A reexecução do 3.1 Flash-Lite reproduziu o resultado da primeira execução, o que indica estabilidade dos modelos nessa tarefa.

**Alternativas consideradas:** `gemini-3.1-flash-lite` (descartado pelo recall menor, com diferença de custo pequena); `gemini-3.8-flash` (descartado pela lentidão no teste); modelos Claude (fora da comparação: os de custo comparável não trariam ganho de prazo, e os maiores ficariam caros na base inteira).

---

## D-024 · O gabarito manual não é revisado depois da comparação

**Data:** 11/11/2026 · **Etapa:** Etiquetagem

**Decisão:** a etiquetagem manual dos 170 comentários permanece como foi feita, sem revisão (adjudicação) à luz das respostas dos modelos. A medição com o manual v1 é a referência de acerto.

**Contexto:** nas divergências, a etiquetagem manual e a do modelo identificaram o mesmo problema no comentário e escolheram detalhes vizinhos para ele (por exemplo, não recebido e prazo, ou não recebido e itens faltando). O manual v1 não tinha regra de desempate para esses casos.

**Justificativa:** são diferenças de interpretação em fronteiras que o manual não definia, e não etiquetas sem relação com o texto. Que as duas etiquetagens tenham reconhecido o mesmo problema em cada caso é evidência de que o modelo não inventa assuntos ausentes do comentário. Revisar o gabarito depois de ver as respostas do modelo tenderia a favorecê-lo.

**Alternativas consideradas:** revisar as divergências com as regras do manual v2 e reportar uma medição adjudicada ao lado da original (descartada: o ganho de informação é pequeno diante do risco de favorecer o modelo).

---

## D-025 · Manual de etiquetagem, versão 2

**Data:** 11/11/2026 · **Etapa:** Etiquetagem

**Decisão:** o manual v2 acrescenta quatro regras de desempate e ajusta as definições correspondentes: produto que ainda não chegou é entrega · não recebido, mesmo citando o prazo, e entrega · prazo negativo é para pedido que chegou atrasado; parte do pedido que não veio é entrega · itens faltando; nota fiscal citada apenas como prova de outro problema não recebe a etiqueta de nota fiscal; elogio à compra, à loja ou ao site como um todo é elogio geral · sem assunto. O manual fica em `reports/lista_temas/manual_v2.json` e é o usado na etiquetagem da base inteira.

**Contexto:** a comparação entre a etiquetagem manual e a dos modelos mostrou que as divergências se concentram nessas fronteiras, com destaque para a confusão entre não recebido e prazo.

**Justificativa:** as regras transformam em critério escrito as decisões que, no manual v1, dependiam de interpretação. Como foram escritas a partir das divergências da amostra de 170 comentários, uma nova medição nessa mesma amostra seria otimista e não substitui a medição com o manual v1.

---

## D-026 · Etiquetagem da base inteira e correção dos sentidos não permitidos

**Data:** 11/11/2026 · **Etapa:** Etiquetagem

**Decisão:** o `gemini-3.5-flash-lite` etiquetou os 40.518 comentários com o manual v2, sem trecho nem justificativa, em lotes de 50 comentários e 8 chamadas simultâneas, com cada lote gravado para retomada. As etiquetas com sentido não permitido pelo manual foram corrigidas sobre o resultado gravado, sem nova chamada ao modelo: avaria no transporte, itens faltando, retirada na agência e nota fiscal com sentido positivo passam para o detalhe "outro" do mesmo tema; o tema "elogio geral" passa a se chamar "geral", e o detalhe "sem assunto" aceita os dois sentidos. O resultado fica em `data/processed/etiquetas_base.parquet`, com uma linha por etiqueta e a coluna `corrigida`.

**Contexto:** a execução levou 14 minutos e custou US$ 9,07, sem lotes com erro e sem comentários sem resposta: 39.491 comentários receberam ao menos uma etiqueta (1,56 por comentário, em média) e 1.027 ficaram sem etiqueta. 1.097 etiquetas (1,8%) saíram com sentido não permitido. A leitura desses comentários mostrou elogios sem lugar no manual ("chegou bem embalado e intacto", "veio tudo certinho", "veio com nota fiscal") e reclamações genéricas ("não recomendo", "loja não é confiável").

**Justificativa:** são lacunas do manual, e não erros de leitura do modelo. O elogio sem defeito cabe no "outro" do tema, que já aceita o sentido positivo. A reclamação genérica é o espelho do elogio genérico e continua sendo um sinal de insatisfação; descartá-la esconderia esses clientes da contagem de atritos.

**Limitações:** cerca de 3 das 44 etiquetas levadas para "outro" eram reclamações com o sentido trocado (por exemplo, "São dois produtos, recebi um"); ficam como resíduo. O `gemini-3.5-flash-lite` ignora o parâmetro de temperatura e usa amostragem fixa, então uma nova execução pode produzir etiquetas diferentes; a reprodução exata depende dos lotes gravados.

**Alternativas consideradas:** marcar as reclamações genéricas como sem etiqueta (descartada: perde a insatisfação declarada); etiquetar de novo os comentários afetados com um manual corrigido (descartada: a correção direta é determinística e não tem custo).

---

## D-027 · Mapa das etiquetas em 3D

**Data:** 11/11/2026 · **Etapa:** Etiquetagem

**Decisão:** um grafo 3D interativo mostra as etiquetas e as ligações entre elas. Cada ponto é uma combinação de sentido, tema e detalhe, com tamanho pela quantidade de comentários e cor vermelha (negativo) ou verde (positivo), com intensidade pela nota média na régua de 1 a 5. Cada linha liga duas etiquetas que aparecem no mesmo comentário, com grossura pela quantidade de comentários. O comprimento da ligação segue o lift: quanto mais as duas etiquetas aparecem juntas acima do esperado se fossem independentes, mais perto ficam. O filtro de sentido começa nas negativas. Os percentuais usam como base os 40.518 comentários. Etiquetas e ligações com menos de 30 comentários ficam fora. A página `reports/visualizacao/grafo_etiquetas.html` é gerada pelo desenv_04 a partir de `src/visualizacao/modelo_grafo.html`, em React com `react-force-graph-3d`, e abre no navegador sem instalação.

**Contexto:** a contagem por etiqueta mostra o tamanho de cada problema, mas não quais problemas andam juntos.

**Justificativa:** a contagem bruta de ligações aproximaria os pontos grandes de todos os outros só pelo volume. O lift corrige isso e forma aglomerados de problemas associados de fato, como não recebido com contato sem resposta (3,6 vezes o acaso) e retirada na agência com frete (21 vezes). A régua absoluta de nota mantém visíveis as exceções, como a etiqueta positiva de cancelamento, troca e reembolso, com nota média 2,6.

**Alternativas consideradas:** distância pela contagem bruta (descartada pelo efeito do volume); régua de cor pela faixa observada em cada sentido (descartada: nos positivos, a faixa de 4,5 a 4,8 exageraria diferenças pequenas).

---

## D-028 · Índice de busca dos comentários

**Data:** 12/11/2026 · **Etapa:** Índice de busca

**Decisão:** cada comentário é um documento, sem divisão em pedaços. Só o texto (título e comentário) vira vetor; nota, mês, estado, região, faixa de atraso, categorias e etiquetas vão junto como informação anexa, usada nos filtros. Os vetores vêm do `gemini-embedding-2` com 768 números por comentário, com o prefixo de documento ("title: ... | text: ...") nos comentários e o prefixo de busca ("task: search result | query: ...") nas perguntas, como pede a documentação do modelo. O índice é um FAISS de busca exata (`IndexFlatIP`, produto interno igual ao cosseno, já que os vetores saem normalizados), montado pelo LangChain e gravado em `data/processed/indice_busca/`. A função `buscar` aplica os filtros antes da busca (etiqueta, sentido, tema, detalhe, nota, estado, região, faixa de atraso, categoria e período) e diversifica os resultados pela relevância marginal máxima (MMR) sobre 500 candidatos, com peso 0,3 para relevância. Com filtro de etiqueta, tema ou detalhe, a diversificação é feita sem corte; sem esse filtro, só entram na escolha os candidatos com similaridade até 0,05 abaixo da do primeiro resultado.

**Contexto:** a vetorização dos 40.518 comentários usou 919.767 tokens e custou cerca de US$ 0,18. O limite de 3.000 textos por minuto do plano pago exigiu lotes de 100 com 4 chamadas simultâneas e novas tentativas com espera; cada lote fica gravado e a execução pode ser retomada. A base tem muitos comentários quase iguais ("produto não foi entregue"), e a busca simples devolve cópias da mesma frase.

**Justificativa:** o teste com 12 perguntas, cada uma com a etiqueta esperada, mediu o acerto (resultados com a etiqueta certa entre os 10 primeiros) e a variedade (1 menos a similaridade média entre esses resultados):

| Versão | Acerto | Variedade |
|---|---|---|
| sorteio de comentários | 7% | |
| busca simples | 99% | 0,07 |
| diversificação sem corte | 81% | 0,21 |
| diversificação moderada (200 candidatos, peso 0,5) | 91% | 0,16 |
| diversificação com corte de 0,05 | 96% | 0,11 |
| com corte e filtro de sentido | 97% | 0,11 |

A diversificação sem corte alcança variedade escolhendo comentários de assuntos vizinhos. O corte descarta esses candidatos antes da escolha. Sem filtro de etiqueta, o projeto prioriza o acerto, porque um comentário fora do assunto apresentado como evidência compromete a resposta. Com filtro de etiqueta, o assunto já está garantido pelo filtro, e a diversificação sem corte acrescenta variedade. Nas perguntas 4 e 5 do enunciado, a regra devolveu oito queixas de assuntos diferentes (filtro de sentido negativo) e oito relatos diferentes de atraso (filtro da etiqueta de prazo); sem o filtro de etiqueta, três dos oito relatos de atraso eram de produtos não recebidos.

**Limitações:** o índice (cerca de 137 MB) e os vetores não são versionados; o notebook os reconstrói com a chave do Google, e a reconstrução refaz as chamadas pagas. A pergunta mais difícil do teste é a de atraso (80% com corte e filtro de sentido), na mesma fronteira entre atraso e não recebido da etiquetagem. O pacote `langchain-community`, que contém o FAISS do LangChain, está sendo descontinuado; a troca por um pacote dedicado fica como evolução.

**Alternativas consideradas:** colocar nota, estado e etiquetas no texto vetorizado (descartada: mistura filtro com sentido e prejudica a busca por assunto); busca aproximada (descartada: 40 mil vetores cabem na busca exata, sem perda de precisão); só a busca simples (descartada: devolve cópias); só a diversificação sem corte (descartada: 81% de acerto sem filtro de etiqueta).

---

## D-029 · Consulta com campos fechados, busca de evidência e fluxo em grafo

**Data:** 12/11/2026 · **Etapa:** Ferramentas e fluxo

**Decisão:** o sistema tem duas ferramentas. `consultar_base` recebe um formulário (Pydantic) com campos fechados: a medida (quantidade de comentários, nota, dias de atraso, prazo de entrega, distância, frete, valor dos produtos), o agrupamento (sentido, tema, detalhe, etiqueta, pares de etiquetas, mês, estado, região, categoria, nota, situação da entrega), os filtros e, opcionalmente, um segundo grupo para comparação. O código valida o formulário e o executa em pandas, devolvendo a tabela e um rastro com cada operação, o código correspondente e as linhas restantes. `buscar_comentarios` é a busca da D-028, usada de dois jeitos: como resposta, quando a pergunta pede as avaliações, e como prova de uma consulta, com dois comentários dentro de cada um dos três primeiros grupos da tabela, ligação feita pelo código. As duas ferramentas partem do mesmo recorte, então o número da resposta e os comentários citados saem do mesmo conjunto.

O `gemini-3.5-flash-lite` lê a pergunta e preenche uma interpretação (`with_structured_output`): o tipo (consulta, busca, fora do tema ou sem dado) e o formulário correspondente. Um formulário recusado pela validação volta ao modelo com o erro, uma vez. O fluxo é um grafo do LangGraph com dez nós: interpretar, consultar, buscar, verificar, provar, coletar, redigir, conferir, recusar e finalizar. A verificação separa o recorte em três faixas: nenhum comentário (recusa), de 1 a 29 (amostra pequena: sem percentual nem ranking, até 10 comentários e aviso de que são poucos para concluir um padrão) e 30 ou mais (resposta completa). O modelo redige a resposta citando os comentários por número; o código confere se cada citação existe (uma nova redação se não existir) e se cada número escrito aparece no contexto (aviso no rastro), e anexa o texto original dos comentários citados sob "Alguns exemplos do que os clientes dizem:". Cada pergunta grava uma linha em `data/processed/registro_respostas.jsonl`. O código da busca foi reunido em `src/busca.py`, com o filtro `todas_etiquetas` para provar os pares de etiquetas.

**Contexto:** o escopo previa seis ferramentas, uma por tipo de pergunta. Na discussão da etapa, a proposta foi um único construtor de consultas, em que o modelo traduz a pergunta e o código executa.

**Justificativa:** o formulário fechado dá a flexibilidade do construtor de consultas sem o risco da consulta livre: um pedido fora das opções (vendedor, centro de distribuição) é barrado antes de qualquer conta e vira recusa, em vez de um número errado com aparência de certo. Cada opção leva uma descrição lida pelo modelo, que diz o que a medida é e o que ela não é. As regras de cálculo ficam no código: dias de atraso só contam pedidos entregues depois da data prevista (53% das queixas de prazo chegaram dentro da data prometida, então a etiqueta mede a percepção e a data mede o atraso), e grupos com menos de 30 comentários saem do resultado com aviso. A amostra pequena, em vez da recusa, preserva a informação de recortes estreitos e continua reconhecendo que eles não sustentam um padrão.

No teste com 18 perguntas, o modelo preencheu os 17 formulários com gabarito como esperado, depois de quatro ajustes nas instruções: "o que os clientes relatam" é consulta; nota baixa é 1 e 2; numa comparação, sem agrupamento; e nota não é sentido, com dois exemplos. As oito perguntas do enunciado passaram pelo grafo inteiro com resposta completa, sem citação inválida nem número fora do contexto, a US$ 0,013 no total; as respostas estão em `reports/respostas/exemplos_enunciado.md`.

**Limitações:** o modelo ignora a temperatura, então a mesma pergunta pode ser interpretada de outro jeito em outra execução. As regras de interpretação foram ajustadas sobre as mesmas perguntas do teste, o que torna o 17 de 17 otimista; a avaliação da etapa 7 usa perguntas novas e repetições. A conferência de números aceita qualquer número presente no contexto, inclusive os dos comentários, e um arredondamento para inteiro. Perguntas ambíguas ("entregas insatisfatórias") recebem uma das leituras possíveis, declarada no início da resposta. A divergência entre nota e texto, prevista no escopo, ficou fora do MVP.

**Alternativas consideradas:** uma ferramenta por tipo de pergunta (descartada: rígida, cada pergunta nova exige uma ferramenta); consulta livre escrita pelo modelo em SQL ou pandas (descartada: erro silencioso e execução de código vindo do texto do usuário); o modelo escolhendo e chamando as ferramentas sozinho com `bind_tools` (descartada: o caminho de cada pergunta fica menos previsível, e a prova da consulta dependeria do modelo lembrar de buscar); recusar todo recorte com menos de 30 comentários (descartada: perde a informação que existe).

---

## D-030 · Avaliação com perguntas novas, três rodadas e juiz automático

**Data:** 12/11/2026 · **Etapa:** Avaliação

**Decisão:** o sistema da etapa 6 é avaliado com 25 perguntas novas, que não foram usadas em nenhum ajuste, em sete grupos: ranking e tema (6, três delas do contexto do enunciado), metadados (5), medidas e comparação (3), padrões e evolução (2), busca direta (3), amostra pequena (2) e recusa (4). Cada pergunta tem um gabarito escrito e congelado antes da execução: o tipo, a faixa do recorte e, quando há formulário, a medida, o agrupamento e o recorte esperados, com alternativas quando mais de uma leitura é razoável. Cada pergunta roda três vezes pelo grafo inteiro. As métricas automáticas conferem a interpretação, a estabilidade entre as rodadas, as recusas, a faixa do recorte, as citações e os números. A fundamentação é julgada pelo `gemini-3.8-flash`, maior e diferente do modelo que escreve as respostas, nas 21 respostas escritas da primeira rodada: cada afirmação é sustentada, parcialmente sustentada ou não sustentada pelo contexto que o sistema recebeu. O código aprovado no desenv_06 foi promovido para `src/fluxo.py`, sem mudança de lógica, e é ele que a avaliação e a aplicação importam.

**Contexto:** os testes da etapa 6 usaram as mesmas perguntas para construir e ajustar as instruções, o que torna o resultado deles otimista. O modelo ignora a temperatura e pode interpretar a mesma pergunta de formas diferentes em execuções diferentes. As conferências do código verificam a forma da resposta, e não se as afirmações são sustentadas pelos comentários citados.

**Justificativa:** as perguntas novas e o gabarito congelado medem o sistema como ele vai ser usado; as três rodadas medem a variação; o juiz cobre o critério que o enunciado mais destaca, respostas coerentes com as evidências.

| Critério | Resultado |
|---|---|
| interpretação igual ao gabarito | 96% (72 de 75 execuções) |
| mesma interpretação nas três rodadas | 96% (24 de 25 perguntas) |
| recusa só quando devia | 99% (74 de 75) |
| faixa do recorte certa | 98% (65 de 66) |
| citações válidas e números presentes no contexto | 100% (75 de 75) |
| afirmações sustentadas (juiz) | 98% (114 de 116) |
| respostas fundamentadas (juiz) | 90% (19 de 21) |
| respostas que respondem à pergunta (juiz) | 95% (20 de 21) |

Os três erros de interpretação são da mesma pergunta (comparação do gasto de quem reclama e de quem elogia a qualidade): em duas rodadas, o modelo agrupou por sentido dentro da etiqueta, caminho que separa os mesmos dois grupos, e na terceira recusou por falta de dado. A resposta não fundamentada citou, como exemplo de demora, um comentário com a etiqueta de prazo que fala de um produto que não funciona: um erro de etiquetagem que passou para a resposta. Nenhuma resposta inventou causa, fato ou número. A avaliação custou US$ 0,21 (US$ 0,10 nas 75 execuções e US$ 0,11 no juiz).

**Limitações:** por decisão de prazo, o veredito do juiz foi tomado como correto, sem uma amostra julgada à mão para medir a concordância. O gabarito é estrito: o caminho equivalente da pergunta 14 conta como erro (com ele, a interpretação iria a 99%). O resultado vale para estas 25 perguntas. A prova de uma consulta confia na etiqueta do comentário; uma conferência entre o texto e o grupo, ou mais comentários por grupo, reduziria o risco visto na resposta não fundamentada.

**Alternativas consideradas:** julgamento manual de uma amostra para validar o juiz (descartada por prazo); o próprio `gemini-3.5-flash-lite` como juiz (descartada: o modelo julgaria as próprias respostas); avaliar só com as perguntas da etapa 6 (descartada: foram usadas nos ajustes).

---

## D-031 · Aplicação de consulta em Streamlit, com o caminho no grafo

**Data:** 12/11/2026 · **Etapa:** Interface

**Decisão:** a aplicação é uma página em Streamlit (`app.py`, na raiz do projeto) que importa o mesmo grafo da avaliação (`src/fluxo.py`), carregado uma vez quando a aplicação abre. A página tem, de cima para baixo: o título e a identificação do trabalho; o campo de pergunta, com as cinco perguntas de exploração do enunciado como atalhos na barra lateral; um acordeão que mostra cada etapa do grafo no momento em que ela roda e, ao fim, recolhe com o número de etapas, o tempo e o custo; a resposta, com a linha do recorte, o texto, um gráfico de barras da tabela calculada e os comentários citados com o texto original, a nota, o estado, o mês e as etiquetas; o desenho do grafo com o caminho percorrido; e um painel de detalhes técnicos (pergunta transformada, código da consulta, buscas, contexto enviado ao modelo e conferências). No desenho do grafo, cada nó é um cartão com ícone; os nós e as setas percorridos ficam em destaque, numerados na ordem, com o resultado da etapa no subtítulo, e o restante fica apagado; ao passar o mouse, cada nó mostra a sua função e o que fez naquela pergunta. O gráfico tem título, subtítulo com o recorte, rótulo em cada barra e tamanho fixo, para não esticar com a tela. A aplicação roda localmente (`streamlit run app.py`).

**Contexto:** o enunciado pede que a solução mostre a transformação da pergunta, a recuperação, a seleção dos conteúdos, o contexto enviado ao modelo e a resposta final, e que o vídeo demonstre a solução com as evidências recuperadas.

**Justificativa:** o acordeão e o desenho do grafo tornam visível o caminho de cada pergunta: uma consulta acende interpretar, consultar, verificar, provar, redigir, conferir e finalizar; uma recusa acende interpretar, recusar e finalizar. Os detalhes técnicos ficam um clique abaixo, para quem quiser conferir o código e o contexto. Na tela, a recusa troca o cardápio técnico do fluxo pelo resumo em linguagem simples do que o sistema responde.

**Limitações:** a aplicação não é publicada. Publicar exigiria subir o índice de busca (cerca de 137 MB, fora do repositório) e expor a chave do Google num servidor; o README explica como reproduzir localmente. Os ícones do grafo vêm de uma biblioteca carregada pela internet, que a aplicação já exige para chamar o modelo.

**Alternativas consideradas:** lista de etapas em texto no lugar do desenho do grafo (descartada: o desenho mostra o caminho e os desvios num relance); cartões com os três primeiros números no lugar do gráfico (descartada: só servem para ranking, e o gráfico atende também à série no tempo e à comparação); publicação no Streamlit Community Cloud (descartada pelos motivos acima).
