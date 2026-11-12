# Exemplos de perguntas e respostas

Gerado pelo `desenv_06_ferramentas_fluxo.ipynb` (passo 6), com o modelo `gemini-3.5-flash-lite`. As perguntas são os exemplos do enunciado do Tech Challenge.

## Investigação de reclamações

**Pergunta:** Quais são os principais problemas relatados pelos clientes em suas avaliações?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'negativo'}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; avaliações de 2016-10 a 2018-08: 15.969 comentários

Os principais problemas relatados envolvem falhas logísticas e divergências nos itens, lembrando que os percentuais são sobre os comentários do recorte e um comentário pode ter mais de uma etiqueta. O principal problema é "entrega · não recebido", presente em 4.101 comentários (25,7%), com clientes relatando ausência de recebimento e de contato [1], [2]. Em seguida, destacam-se "produto · conformidade com o anúncio" com 3.141 comentários (19,7%), onde compradores apontam o recebimento de itens errados e cores diferentes do anunciado [3], [4], e "produto · qualidade" com 2.659 comentários (16,7%), que engloba defeitos e dificuldades no uso [5], [6].

| grupo | comentários | % do recorte |
|---|---|---|
| entrega · não recebido | 4.101 | 25,7% |
| produto · conformidade com o anúncio | 3.141 | 19,7% |
| produto · qualidade | 2.659 | 16,7% |

Alguns exemplos do que os clientes dizem:
[1] "Produto não foi entregue e não entraram em contato para dá uma posição. Dificuldades para resolução do problema!" (nota 1, RJ, 2017-12)
[2] "Comprei duas vezes porta cds, de vocês na lannister nesse mês, e não recebi nenhum porta cds. Peço que corrijam esse erro gravissímo, pois gostaria de continuar sendo cliente lannister." (nota 1, SP, 2017-03)
[3] "Recebi o produto errado e a central de atendimento é muito ruim, não consigo entrar em contato, respondem email quando querem e não resolvem meu problema!" (nota 1, SP, 2018-07)
[4] "as cores nao sao da propaganda" (nota 1, MG, 2018-03)
[5] "O produto está com problemas (defeito)." (nota 2, SP, 2017-12)
[6] "Achei o frete meio caro, por ser um produto leve. A capa atrapalha um pouco o uso do sensor biometrico e é dificil retirar a ultima camada da pelicula, durante a aplicação;" (nota 4, MG, 2018-01)

## Investigação de um tema específico

**Pergunta:** O que os clientes relatam sobre problemas relacionados à entrega?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'negativo', 'tema': ['entrega']}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; tema entrega; avaliações de 2016-10 a 2018-08: 9.531 comentários

O principal problema relatado é que o produto não foi recebido, presente em 4.101 menções (43,0%), com clientes apontando que a mercadoria não chega ou ultrapassa a data prevista [1], [2]. Além disso, os clientes destacam problemas de itens faltando, representando 2.508 comentários (26,3%), onde pacotes chegam incompletos [3] ou trazem apenas brindes sem o produto principal [4]. As reclamações sobre prazo somam 1.683 menções (17,7%), evidenciando atrasos e falhas no rastreio [5], [6]. Como um comentário pode ter mais de uma etiqueta, os percentuais são sobre os comentários do recorte e não somam 100%.

| grupo | comentários | % do recorte |
|---|---|---|
| entrega · não recebido | 4.101 | 43,0% |
| entrega · itens faltando | 2.508 | 26,3% |
| entrega · prazo | 1.683 | 17,7% |

Alguns exemplos do que os clientes dizem:
[1] "tive problemas com a entrega a mercadoria não foi entrgue" (nota 2, PE, 2017-09)
[2] "Antecipei a compra para um presente de aniversário, e passado o dia previsto para a entrega o produto ainda não chegou. A festa é neste sábado. Será que chegarei de mãos vazias?" (nota 1, SP, 2017-03)
[3] "a entrega nao chegou correta completa" (nota 1, SP, 2018-06)
[4] "ENTREGARAM APENAS UM BRINDE ACOMPANHADO DE UMA CARTA, EXPLICANDO QUE HOUVE PROBLEMAS NA FABRICA DA CALOI E AGORA NÃO SEI QUAL SERÁ O NOVO PRAZO PARA A ENTREGA" (nota 1, MS, 2018-02)
[5] "demora na entrega." (nota 4, SP, 2017-07)
[6] "Não recebi meu produto e só atualizaram o rastreio depois do prazo de entrega acabar. Correio mentiu dizendo que me neguei à receber. Quero meu dinheiro de volta, inclusive o frete." (nota 1, RJ, 2017-12)

## Busca por experiências positivas

**Pergunta:** Quais aspectos da experiência de compra são mais elogiados pelos clientes?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'positivo'}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido positivo; avaliações de 2016-10 a 2018-08: 26.425 comentários

Os aspectos mais elogiados pelos clientes são o grupo geral · sem assunto, presente em 13.396 avaliações (50,7%), e o grupo entrega · prazo, citado em 12.408 comentários (47,0%). Como um comentário pode ter mais de uma etiqueta, os percentuais são sobre o total do recorte e não somam 100%. Os clientes destacam a perfeição e o bom acabamento dos produtos [2], além do serviço de entrega perfeito e dentro do prazo [3], [4]. A qualidade do produto também aparece com relevância, somando 8.753 menções (33,1%) [5], [6].

Alguns exemplos do que os clientes dizem:
[2] "Os detalhes dos quadros são lindos, super bem feitos e acabados, amei!" (nota 5, SC, 2017-11)
[3] "Produto muito bom, custo de acordo e serviço de entrega perfeito. Só tenho elogios a fazer a toda a operação!" (nota 5, SP, 2018-06)
[4] "estão de parabéns com a pontualidade de você" (nota 5, RJ, 2017-03)
[5] "produto muito bom e bem feito. Recebi muito bem embalado. Super recomendo." (nota 5, RS, 2018-08)
[6] "Facilidade em manusear o aparelho." (nota 4, SP, 2016-10)

## Investigação de insatisfação

**Pergunta:** Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'etiquetas_juntas', 'filtros': {'sentido': 'negativo'}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; avaliações de 2016-10 a 2018-08: 15.969 comentários

Os percentuais apresentados referem-se aos comentários do recorte, e como um comentário pode ter mais de uma etiqueta, eles não somam 100%. A coluna lift indica quantas vezes o par aparece junto acima do esperado pelo acaso, sendo que o valor 1 representa o acaso. O principal destaque da tabela é o grupo de entrega por retirada na agência combinado com preço e frete, que soma 111 menções (0,7%) e apresenta um lift de 8,3, refletindo a insatisfação de clientes que pagaram o frete e ainda precisaram buscar os produtos nos correios [1], [2]. O segundo maior destaque é a combinação entre preço do produto e qualidade, com 96 ocorrências (0,6%) e lift de 2,7, evidenciando críticas de que itens caros possuem qualidade péssima [3] ou material abaixo do esperado pelo preço [4]. Já as falhas de atendimento ligadas a cancelamentos, trocas e reembolsos aparecem associadas à falta de contato e resposta, somando 227 casos (1,4%) com lift de 1,4, o que demonstra frustração com a falta de atenção e dificuldade para efetuar trocas [5], [6].

| grupo | comentários | % do recorte | lift |
|---|---|---|---|
| entrega · retirada na agência + preço · frete | 111 | 0,7% | 8,3 |
| preço · preço do produto + produto · qualidade | 96 | 0,6% | 2,7 |

Alguns exemplos do que os clientes dizem:
[1] "comprei paguei o frete, e tive que buscar no correio, como posso esta satisfeito, e pior abri uma reclamação e estou até hoje esperando uma resposta do MarketPlace." (nota 1, SP, 2016-11)
[2] "Nao recomendo pessima qualidade,ja veio com o assento rasgado a parte branca encardida de tao empuerada que veio paguei o frete caro e nao recebi em casa tive que ir busca." (nota 1, PB, 2018-07)
[3] "A loja vende um produto muito caro mas a qualidade é péssima" (nota 1, SP, 2018-08)
[4] "Gostei da entrega, chegou bem antes do prazo, mas o material do estojo pensei que fosse melhor devido ao preço que saiu com frete, por isso dou 3 estrelas." (nota 3, MG, 2017-12)
[5] "Estou insatisfeita pela falta de atenção com o cliente! Foi solicitado no início o cancelamento do pedido no qual não fui atendida! Não pretendo comprar mais tão cedo por aqui! !!" (nota 2, DF, 2018-04)
[6] "ENTREGARAM O LIVRO ERRADO NÃO CONSIGO CONTACTAR NINGUÉM DA lannister. O SISTEMA NÃO ACEITA QUANDO TENTO CADASTRAR A TROCA PELO LIVRO CORRETO. ENTREM EM CONTATO COMIGO!!" (nota 1, RJ, 2018-07)

## Exploração baseada em evidências

**Pergunta:** Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

**Como o sistema entendeu:** tipo busca: `{'texto': 'problemas recorrentes prazo de entrega', 'filtros': {'sentido': 'negativo', 'tema': ['entrega'], 'detalhe': ['prazo']}, 'quantidade': 10}`

**Caminho no grafo:** interpretar → buscar → verificar → coletar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; tema entrega; detalhe prazo; avaliações de 2016-10 a 2018-08: 1.683 comentários

Os clientes apontam em comum o descumprimento do prazo estimado e falhas no rastreamento ou na comunicação, como visto em [1], [2], [3], [5], [8] e [9]. As opiniões diferem quanto ao histórico de compra e à gravidade da demora, variando desde um atraso pontual que frustrou datas comemorativas até casos extremos de meses de espera [6], além de exceções onde o serviço costuma ser pontual [4], [10] e urgências não atendidas [7]. Como um comentário pode ter mais de uma etiqueta, os percentuais não somam 100%.

Comentários encontrados:
[1] "entrega fora do prazo" (nota 3, SP, 2018-03)
[2] "a Quase 20 dias aparece no rastreamento dificuldade na entrega, ja mandei mensagens e nada fora feito...ja esta em atraso de 5 dias da data prevista e sem providencia do site das lannister.. fazer" (nota 1, RS, 2018-04)
[3] "Precisa melhorar no prazo de entrega, deveriam deixar de trabalhar com os correios o mesmo esta deixando muito a deseja." (nota 3, ES, 2018-05)
[4] "Os produtos vendidos e entregues diretamente pelo baratheon são sempre entregues antes do prazo estimado. Este pedido está sendo uma exceção." (nota 4, RJ, 2018-04)
[5] "Todas as etapas de entrega tiveram um problema, o objeto chegou com atraso em tudo e até agora consta que não chegou à unidade do rio de janeiro, sendo que era pra eu ter recebido o produto no dia 10" (nota 1, RJ, 2018-04)
[6] "A Reclamação é que demorou para entregarem o produto, comprei com quase 2 meses de antecedência, totalizando 3 meses para entrega do mesmo. Data não condiz com a entrega verdadeira. Lamentável." (nota 1, RS, 2017-12)
[7] "PRECISO COM URGÊNCIA DESTE PRODUTO, ESTA DEMORANDO DEMAIS, FAVOR ME RETORNAREM COM URGÊNCIA QUANTO A ESTA ENTREGA" (nota 1, RS, 2017-12)
[8] "O prazo para entrega do produto seria 02/01/2018 O produto consta "aguardando nota fiscal " O prazo não foi cumprido e não existe uma nova data para entrega ." (nota 1, SP, 2018-01)
[9] "Prazo de 3 dias úteis para entrega. Foi Comprado para presente do dia dos pais 06/08, 4 dias para entregar e não foi entregue! Se não consegue entregar no prazo aumente os dias !!!" (nota 2, SP, 2018-08)
[10] "sou cliente faz anos, é a 1ª vez que acontece atraso de entrega de mercadorias" (nota 4, PB, 2018-03)

## Metadado: nota

**Pergunta:** Quais são os principais problemas relatados nas avaliações com nota baixa?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'negativo', 'nota': [1, 2]}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; nota 1, 2; avaliações de 2016-10 a 2018-08: 10.423 comentários

| grupo | comentários | % do recorte |
|---|---|---|
| entrega · não recebido | 3.614 | 34,7% |
| produto · conformidade com o anúncio | 1.962 | 18,8% |
| entrega · itens faltando | 1.861 | 17,9% |

Os percentuais são calculados sobre os comentários do recorte, e como um comentário pode ter mais de uma etiqueta, eles não somam 100%. Os principais problemas relatados nas notas baixas concentram-se na falha de entrega por não recebimento com 34,7% [1], [2], divergências na conformidade do produto com o anúncio somando 18,8% [3], [4] e itens faltando na entrega atingindo 17,9% [5], [6]. Os clientes apontam dificuldades como rastreamento desatualizado [2], recebimento de itens com especificações erradas [4] e falta parcial ou total de mercadorias nos pedidos [1], [5], [6].

Alguns exemplos do que os clientes dizem:
[1] "Dei nota baixa pois sao dois pedidos e o outro do aparelho celular veio faltando 1 e até agora não recebi 😡" (nota 1, SP, 2017-10)
[2] "Comprei dois produtos distintos da targaryen pelo stark. Em ambos houve dificuldade na entrega e rastreamento não atualiza há semanas." (nota 1, AL, 2018-02)
[3] "Produto de baixa qualidade x preco x descrição do produto" (nota 2, RS, 2017-12)
[4] "Recebi as lentes de contato com o grau errado. Solicitei 1.50 e vieram com 1.75. Triste pois preciso das lentes para sábado dia 19/05." (nota 1, SP, 2018-05)
[5] "Dei nota baixa pois sao dois pedidos e o outro do aparelho celular veio faltando 1 e até agora não recebi 😡" (nota 1, SP, 2017-10)
[6] "FALTOU CADEIRAS" (nota 2, RJ, 2018-04)

## Metadado: categoria

**Pergunta:** O que os clientes mais elogiam na categoria cama, mesa e banho?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'positivo', 'categoria': ['cama mesa banho']}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido positivo; categoria cama mesa banho; avaliações de 2016-10 a 2018-08: 2.697 comentários

Os clientes elogiam principalmente a satisfação geral, a qualidade do produto e o cumprimento do prazo de entrega, lembrando que os percentuais são sobre os comentários do recorte e um comentário pode ter mais de uma etiqueta. O grupo geral sem assunto aparece em 1.400 avaliações (51,9%), seguido por produto · qualidade com 1.097 (40,7%) e entrega · prazo com 1.014 (37,6%). Os compradores destacam que os itens ficam muito bonitos na cama [1], [3], demonstram satisfação com a qualidade e a pontualidade [4], [5], além de elogiarem entregas antes do prazo estipulado [2], [5], [6]. 

| grupo | comentários | % do recorte |
|---|---|---|
| geral · sem assunto | 1.400 | 51,9% |
| produto · qualidade | 1.097 | 40,7% |
| entrega · prazo | 1.014 | 37,6% |

Alguns exemplos do que os clientes dizem:
[1] "Valeu a pena a compra. Fica muito bonito na cama" (nota 5, SP, 2017-07)
[2] "Amei o produto, chegou 2 dias antes do prazo, parabéns lannister por essa parceria com essa transportadora tão boa, continuarei comprando sempre, obrigada a todos." (nota 5, SP, 2018-08)
[3] "Valeu a pena a compra. Fica muito bonito na cama" (nota 5, SP, 2017-07)
[4] "Satisfação com os produtos e tudo entregue no tempo certo. Obrigada!" (nota 4, SP, 2018-08)
[5] "Produto de ótima qualidade, ficou perfeita na minha cama. Chegou antes do prazo." (nota 5, SP, 2018-07)
[6] "tudo dentro do prazo; parabens" (nota 5, SC, 2018-03)

## Metadado: entrega

**Pergunta:** Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?

**Como o sistema entendeu:** tipo consulta: `{'agrupar_por': 'detalhe', 'filtros': {'sentido': 'negativo', 'tema': ['entrega']}}`

**Caminho no grafo:** interpretar → consultar → verificar → provar → redigir → conferir → finalizar

**Resposta:**

Recorte: sentido negativo; tema entrega; avaliações de 2016-10 a 2018-08: 9.531 comentários

Os dados mostram que os principais problemas nas experiências de entrega insatisfatórias são a ausência de recebimento, citada em 4.101 comentários (43,0%), e os itens faltando, presentes em 2.508 registros (26,3%). Os clientes relatam que os produtos não chegam [1], [2], que há atrasos consideráveis [2], [5], [6] e que os pedidos vêm incompletos [3], [4]. Vale notar que os percentuais são sobre os comentários do recorte e, como um comentário pode ter mais de uma etiqueta, eles não somam 100%. Além disso, os compradores mencionam falta de satisfação e comunicação [2], e até o recebimento de itens errados [6].

Alguns exemplos do que os clientes dizem:
[1] "o produto ainda não foi entregue" (nota 1, PE, 2018-08)
[2] "Péssimo atendimento, não entregam no prazo, sem qualquer tipo de satisfação ao cliente. Horrível!" (nota 2, RJ, 2018-01)
[3] "a entrega nao chegou correta completa" (nota 1, SP, 2018-06)
[4] "Gostei do design do relógio porém veio sem a caixa e jogado na caixa do correio, na minha opinião cada detalhe é importante principalmente com a fidelização do cliente...." (nota 2, SP, 2018-06)
[5] "demora na entrega." (nota 4, SP, 2017-07)
[6] "FOI ENTREGUE UM PRODUTO DE OUTRA MARCA, O PRAZO NÃO FOI CUMPRIDO, FRETE CARO, ENFIM ESSA COMPRA FOI UM DESASTRE" (nota 1, SP, 2018-05)
