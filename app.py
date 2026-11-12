"""Tech Challenge 4 - Voz do Cliente: aplicação de consulta (etapa 8).

Roda o mesmo grafo da etapa 6 (src/fluxo.py) e mostra, para cada pergunta, o caminho percorrido,
a resposta com os comentários que a sustentam e o rastro de cada etapa.

Como rodar, na raiz do projeto (com a chave do Google no .env e o índice gerado pelo desenv_05):
    streamlit run app.py
"""

import html
import json
import re
import sys
import textwrap
import time
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))  # permite importar o código de src/

st.set_page_config(page_title="Tech Challenge 4 - Voz do Cliente", page_icon="💬", layout="wide")


# ── 1. Carga do fluxo: uma vez só, quando a aplicação abre ───────────────────
@st.cache_resource(show_spinner="Carregando a base, as etiquetas e o índice de busca…")
def carregar_fluxo():
    from src import fluxo  # lê a base, as etiquetas e o índice FAISS e monta o grafo
    fluxo.ARQUIVO_REGISTRO = RAIZ / "data" / "processed" / "registro_app.jsonl"  # registro próprio da aplicação
    return fluxo


fluxo = carregar_fluxo()

PERGUNTAS_EXEMPLO = {
    "Principais problemas": "Quais são os principais problemas relatados pelos clientes em suas avaliações?",
    "Problemas de entrega": "O que os clientes relatam sobre problemas relacionados à entrega?",
    "O que mais elogiam": "Quais aspectos da experiência de compra são mais elogiados pelos clientes?",
    "Padrões dos insatisfeitos": "Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?",
    "Avaliações sobre prazo": "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
}

CAPACIDADES = ("Queixas e elogios por tema e detalhe, filtrados por estado, região, período, nota, categoria e "
               "situação da entrega; padrões de etiquetas que aparecem juntas; nota média, atraso, prazo, "
               "distância, frete e valor dos produtos, inclusive comparando dois grupos.")

# ── 2. Execução com verbose: cada nó aparece enquanto roda ───────────────────
def executar(pergunta):
    """Roda o grafo mostrando cada etapa no acordeão; devolve o estado final e o tempo."""
    comeco = time.perf_counter()
    estado, vistos = None, 0
    with st.status("Executando o fluxo…", expanded=True) as status:
        # stream_mode="values": o grafo devolve o estado completo depois de cada nó
        for estado in fluxo.fluxo.stream({"pergunta": pergunta, "rastro": [], "tokens": []}, stream_mode="values"):
            for linha in estado.get("rastro", [])[vistos:]:  # só as linhas novas do rastro
                st.markdown(f"**{linha['nó']}** · {linha['o que fez']}")
            vistos = len(estado.get("rastro", []))
        segundos = time.perf_counter() - comeco
        status.update(label=resumo_execucao(estado, segundos), state="complete", expanded=False)
    return estado, segundos


def custo(estado):
    entrada = sum(e for e, _ in estado.get("tokens", []))
    saida = sum(s for _, s in estado.get("tokens", []))
    return (entrada * fluxo.PRECO["entrada"] + saida * fluxo.PRECO["saida"]) / 1e6


def resumo_execucao(estado, segundos):
    return (f"Caminho percorrido: {len(estado['rastro'])} etapas · " + f"{segundos:.1f}".replace(".", ",") + " s · US$ "
            + f"{custo(estado):.4f}".replace(".", ","))


# ── 3. Resposta: texto, gráfico e exemplos ───────────────────────────────────
TITULOS_EXEMPLOS = ("Alguns exemplos do que os clientes dizem:", "Comentários encontrados:")


def mostrar_resposta(estado):
    if estado.get("recusa"):
        # na tela, o cardápio técnico do fluxo dá lugar ao resumo em linguagem simples
        motivo = estado["resposta_final"].split("O que o sistema consegue responder:")[0].strip()
        if estado["recusa"] in ("no tema, sem dado", "formulário inválido"):
            motivo += f"\n\n**O que o sistema consegue responder:** {CAPACIDADES}"
        st.warning(motivo.replace("$", r"\$"), icon="🚫")  # "$" escapado: o Streamlit leria como fórmula
        return
    texto = estado["resposta_final"]
    titulo = next((t for t in TITULOS_EXEMPLOS if t in texto), None)
    corpo = texto.split(titulo)[0].strip() if titulo else texto
    st.markdown(corpo.replace("$", r"\$"))
    mostrar_grafico(estado)
    # os exemplos citados, com o texto original anexado pelo código
    comentarios = estado["comentarios"]
    if estado["interpretacao"].tipo == "busca":
        numeros = list(range(1, len(comentarios) + 1))
    else:
        numeros = sorted({int(n) for n in re.findall(r"\[(\d+)\]", corpo) if 1 <= int(n) <= len(comentarios)})
    if numeros:
        st.markdown(f"**{titulo or TITULOS_EXEMPLOS[0]}**")
        for n in numeros:
            c = comentarios.loc[n - 1]
            st.markdown(
                f"<div style='border-left:3px solid #c9d3e3;padding:4px 12px;margin:6px 0;'>"
                f"<span style='color:#8a93a3'>[{n}]</span> {html.escape(c['comentário'])}"
                f"<br><span style='color:#8a93a3;font-size:0.85em'>nota {c['nota']} · {c['estado']} · {c['mês']} · "
                f"{html.escape(c['etiquetas'])}</span></div>", unsafe_allow_html=True)


NOME_MEDIDA = {  # título do gráfico e do eixo para cada medida do formulário
    "comentarios": "Comentários", "nota": "Nota média (1 a 5)", "dias_atraso": "Dias de atraso (média)",
    "prazo_entrega_dias": "Prazo de entrega em dias (média)", "distancia_km": "Distância vendedor-cliente em km (média)",
    "valor_frete": "Frete em R$ (média)", "valor_produtos": "Valor dos produtos em R$ (média)",
}
NOME_AGRUPAMENTO = {
    "sentido": "sentido", "tema": "tema", "detalhe": "detalhe", "etiqueta": "etiqueta", "etiquetas_juntas": "par de etiquetas",
    "mes": "mês", "estado": "estado", "regiao": "região", "categoria": "categoria", "nota": "nota",
    "faixa_atraso": "situação da entrega",
}


def br(valor, casas=1):
    """Número no formato brasileiro: 4.101 e 43,0."""
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def sem_periodo(filtros):
    """Recorte de um grupo, sem a parte do período (que é a mesma nos dois grupos)."""
    partes = [p for p in fluxo.descrever_recorte(filtros).split("; ") if not p.startswith(("avaliações", "base inteira"))]
    return "; ".join(partes) or "base inteira"


def mostrar_grafico(estado):
    """Gráfico de barras da tabela calculada, com título, subtítulo, rótulos e nomes dos eixos."""
    resultado = estado.get("resultado")
    if not resultado or estado.get("faixa") != "completo" or resultado["tabela"].empty:
        return
    consulta = resultado["consulta"]
    tabela = resultado["tabela"].rename_axis("grupo").reset_index()
    comparacao = consulta.comparar_com is not None
    contagem = consulta.medida == "comentarios"
    valor = "comentários" if contagem else "média"

    # o rótulo de cada barra, já no formato brasileiro
    if comparacao:
        tabela["grupo"] = [f"{g}: {sem_periodo(f)}" for g, f in zip(tabela["grupo"], tabela["filtros"])]
    if consulta.agrupar_por == "etiquetas_juntas":
        tabela["rótulo"] = [f"{br(n, 0)} · {br(p)}% · lift {br(l)}" for n, p, l in
                            zip(tabela["comentários"], tabela["% do recorte"] * 100, tabela["lift"])]
    elif contagem:
        tabela["rótulo"] = [f"{br(n, 0)} · {br(p)}%" for n, p in zip(tabela["comentários"], tabela["% do recorte"] * 100)]
    else:
        tabela["rótulo"] = [f"{br(m)} ({br(n, 0)} comentários)" for m, n in zip(tabela["média"], tabela["comentários"])]
    tabela["curto"] = [br(v, 0 if contagem else 1) for v in tabela[valor]]  # rótulo em cima das colunas (série no tempo)
    tabela = tabela[["grupo", valor, "rótulo", "curto"]].astype({"grupo": str})

    # título, subtítulo (o recorte) e a nota sobre o que o número significa
    agrupamento = "grupo" if comparacao else NOME_AGRUPAMENTO.get(consulta.agrupar_por, "recorte")
    titulo = f"{NOME_MEDIDA[consulta.medida]} por {agrupamento}"
    subtitulo = [f"Recorte: {fluxo.descrever_recorte(consulta.filtros.para_busca())}: {br(estado['tamanho'], 0)} comentários"]
    if contagem:
        subtitulo.append("Percentual sobre os comentários do recorte; um comentário pode ter mais de uma etiqueta, então não somam 100%.")
    if consulta.agrupar_por == "etiquetas_juntas":
        subtitulo.append("Lift: quantas vezes o par aparece junto acima do esperado pelo acaso (1 = acaso).")
    # linhas curtas: o gráfico tem largura fixa, e o texto longo seria cortado
    subtitulo = [linha for texto in subtitulo for linha in textwrap.wrap(texto, 78)]
    cabecalho = alt.TitleParams(titulo, subtitle=subtitulo, anchor="start", fontSize=16, subtitleFontSize=12,
                                subtitleColor="#55607a", offset=12)
    maximo = tabela[valor].max()

    if consulta.agrupar_por == "mes":  # série no tempo: colunas na ordem dos meses, rótulo em cima
        base = alt.Chart(tabela, title=cabecalho).encode(
            x=alt.X("grupo:N", title="mês da avaliação", sort=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(f"{valor}:Q", title=NOME_MEDIDA[consulta.medida], scale=alt.Scale(domain=[0, maximo * 1.18]),
                    axis=alt.Axis(format="d")))
        grafico = base.mark_bar(color="#2f6db5", cornerRadiusEnd=3) + base.mark_text(
            dy=-8, fontSize=11, color="#1f2a44").encode(text="curto:N")
        altura = 300
    else:  # ranking: barras deitadas, da maior para a menor, rótulo no fim da barra
        base = alt.Chart(tabela, title=cabecalho).encode(
            # paddingInner: espaço entre as barras (35% da faixa de cada uma)
            y=alt.Y("grupo:N", title=None, sort=None, scale=alt.Scale(paddingInner=0.35),
                    axis=alt.Axis(labelLimit=320, labelOverlap=False, labelPadding=8)),
            x=alt.X(f"{valor}:Q", title=NOME_MEDIDA[consulta.medida], scale=alt.Scale(domain=[0, maximo * 1.3]),
                    axis=alt.Axis(format="d", tickCount=5, grid=False)))
        grafico = base.mark_bar(color="#2f6db5", cornerRadiusEnd=3) + base.mark_text(
            align="left", dx=6, fontSize=12, color="#1f2a44").encode(text="rótulo:N")
        altura = 36 * len(tabela)  # cada barra com 36 px, qualquer que seja a quantidade
    # tamanho fixo, perto da largura da tabela da resposta: não estica com a tela
    # o Streamlit encaixa título, subtítulo e eixo dentro da altura: soma o espaço deles à área das barras
    altura += 40 + 16 * len(subtitulo) + 50
    grafico = (grafico.properties(height=altura).configure_view(stroke=None)
               .configure_axis(labelFontSize=12.5, titleFontSize=12.5, titleColor="#55607a", labelColor="#1f2a44"))
    st.altair_chart(grafico, width=720)


# ── 4. O grafo do caminho: nós acesos onde a pergunta passou ─────────────────
# cada nó: posição do centro (x, y), ícone (Tabler Icons) e subtítulo fixo
NOS = {
    "pergunta":    ((380, 44),  "ti-message-question", "o que o gestor quer saber"),
    "interpretar": ((380, 134), "ti-sparkles",         "modelo preenche o formulário"),
    "consultar":   ((240, 234), "ti-table",            "pandas calcula a tabela"),
    "buscar":      ((520, 234), "ti-search",           "mede o recorte da busca"),
    "recusar":     ((118, 334), "ti-hand-stop",        "explica o limite da base"),
    "verificar":   ((380, 334), "ti-ruler-measure",    "mede o tamanho do recorte"),
    "provar":      ((240, 434), "ti-file-search",      "busca comentários de prova"),
    "coletar":     ((520, 434), "ti-messages",         "traz os comentários pedidos"),
    "redigir":     ((380, 534), "ti-writing",          "modelo escreve a resposta"),
    "conferir":    ((380, 634), "ti-checklist",        "confere citações e números"),
    "finalizar":   ((380, 734), "ti-flag-check",       "resposta, exemplos e registro"),
}
LARGURA, ALTURA = 214, 58

FUNCAO = {  # o papel de cada nó no fluxo: abre o tooltip, antes do que o nó fez nesta pergunta
    "pergunta": "O que o gestor perguntou, em linguagem natural.",
    "interpretar": "O modelo de linguagem (Gemini) lê a pergunta e preenche um formulário fechado: tipo da pergunta, "
                   "medida, agrupamento e filtros. Ele não calcula nada.",
    "consultar": "O código (pandas) executa o formulário na base etiquetada: aplica os filtros, agrupa e calcula. "
                 "Todos os números da resposta saem daqui.",
    "buscar": "Para perguntas que pedem os próprios comentários: mede quantos comentários existem no recorte pedido.",
    "verificar": "Mede o tamanho do recorte e escolhe a faixa: vazio (recusa), amostra pequena (1 a 29 comentários) "
                 "ou completa (30 ou mais).",
    "provar": "Busca por sentido (índice FAISS) dentro dos primeiros grupos da tabela, para que cada número venha "
              "com comentários que o sustentam.",
    "coletar": "Busca por sentido (índice FAISS) dentro do recorte e traz os comentários pedidos, sem repetir histórias iguais.",
    "redigir": "O modelo escreve a resposta usando só a tabela e os comentários entregues, citando cada comentário pelo número.",
    "conferir": "O código confere se cada citação existe e se cada número escrito está no contexto. "
                "Citação inválida volta para uma nova redação.",
    "recusar": "Quando a pergunta está fora do tema, pede um dado que a base não tem ou o recorte está vazio, "
               "explica o limite em vez de inventar uma resposta.",
    "finalizar": "Junta a resposta, anexa o texto original dos comentários citados e grava o registro da pergunta.",
}


def caminho_da_aresta(a, b):
    """Curva da seta entre dois nós (saída e chegada escolhidas para não cruzar outros nós)."""
    (x1, y1), (x2, y2) = NOS[a][0], NOS[b][0]
    meia_l, meia_a = LARGURA / 2, ALTURA / 2
    if (a, b) == ("conferir", "redigir"):  # volta para nova redação, pela direita
        return f"M {x1 + meia_l} {y1} C {x1 + meia_l + 70} {y1}, {x2 + meia_l + 70} {y2}, {x2 + meia_l + 6} {y2}"
    if (a, b) == ("interpretar", "recusar"):  # desce pela esquerda, por fora de "consultar"
        return f"M {x1 - meia_l} {y1} C {x2} {y1}, {x2} {y1 + 60}, {x2} {y2 - meia_a - 6}"
    if (a, b) == ("verificar", "recusar"):
        return f"M {x1 - meia_l} {y1} L {x2 + meia_l + 6} {y2}"
    if (a, b) == ("recusar", "finalizar"):  # desce pela esquerda até o fim
        return f"M {x1} {y1 + meia_a} C {x1} {y2}, {x1 + 60} {y2}, {x2 - meia_l - 6} {y2}"
    ys, yc = y1 + meia_a, y2 - meia_a - 6
    meio = (ys + yc) / 2
    return f"M {x1} {ys} C {x1} {meio}, {x2} {meio}, {x2} {yc}"


ARESTAS = [("pergunta", "interpretar"), ("interpretar", "recusar"), ("interpretar", "consultar"),
           ("interpretar", "buscar"), ("consultar", "verificar"), ("buscar", "verificar"),
           ("verificar", "recusar"), ("verificar", "provar"), ("verificar", "coletar"), ("provar", "redigir"),
           ("coletar", "redigir"), ("redigir", "conferir"), ("conferir", "redigir"), ("conferir", "finalizar"),
           ("recusar", "finalizar")]


def resultado_do_no(no, estado):
    """Subtítulo dinâmico de um nó percorrido: o principal resultado da etapa."""
    interp = estado.get("interpretacao")
    milhar = lambda n: f"{n:,}".replace(",", ".")
    if no == "interpretar":
        return f"tipo: {interp.tipo.replace('_', ' ')}" if interp else "formulário inválido"
    if no in ("consultar", "buscar") and estado.get("tamanho") is not None:
        return f"{milhar(estado['tamanho'])} comentários"
    if no == "verificar":
        return {"completo": "faixa completa", "pequeno": "amostra pequena", "vazio": "recorte vazio"}.get(estado.get("faixa"), "")
    if no in ("provar", "coletar") and estado.get("comentarios") is not None:
        return f"{len(estado['comentarios'])} comentários"
    if no == "redigir":
        tentativas = estado.get("tentativas_redacao", 1)
        return "1 redação" if tentativas == 1 else f"{tentativas} redações"
    if no == "conferir":
        problemas = [n for n in estado.get("citacoes_invalidas", []) if n != 0] or estado.get("numeros_fora")
        return "citações e números ok" if not problemas else "com aviso"
    if no == "recusar":
        return estado.get("recusa", "")
    if no == "finalizar":
        return f"US$ {custo(estado):.4f}".replace(".", ",")
    return NOS[no][2]


def detalhes_do_no(no, estado):
    """Texto do tooltip: o que o nó fez nesta pergunta."""
    if no == "pergunta":
        return [estado["pergunta"]]
    feitos = [l["o que fez"] for l in estado["rastro"] if l["nó"] == no]
    if not feitos:
        return ["não percorrido nesta pergunta"]
    linhas = list(feitos)
    interp = estado.get("interpretacao")
    if no == "consultar" and estado.get("resultado"):
        linhas += [f"→ {p['o que foi feito']} (" + f"{p['linhas']:,}".replace(",", ".") + " linhas)"
                   for _, p in estado["resultado"]["rastro"].iterrows()]
    if no in ("provar", "coletar") and estado.get("buscas") is not None:
        linhas += [f"→ busca em {b['grupo']}: " + f"{b['comentários permitidos']:,}".replace(",", ".") + f" comentários; {b['regra']}"
                   for _, b in estado["buscas"].iterrows()]
    if no == "recusar" and interp is not None and interp.motivo:
        linhas.append(f"motivo: {interp.motivo}")
    return linhas


def desenhar_caminho(estado):
    """Grafo com ícones: nós e setas percorridos em destaque, numerados na ordem; o resto apagado."""
    caminho = ["pergunta"] + [l["nó"] for l in estado["rastro"]]
    percorridas = set(zip(caminho, caminho[1:]))
    ordem = {}
    for no in caminho:  # número da etapa: a primeira vez que o nó aparece
        ordem.setdefault(no, len(ordem))
    setas = []
    for a, b in ARESTAS:
        classe = "seta ativa" if (a, b) in percorridas else "seta"
        if (a, b) in percorridas and "recusar" in (a, b):
            classe += " recusa"
        setas.append(f"<path class='{classe}' d='{caminho_da_aresta(a, b)}' "
                     f"marker-end='url(#{'ponta-recusa' if 'recusa' in classe else 'ponta-ativa' if 'ativa' in classe else 'ponta'})'/>")
    cartoes = []
    for no, ((x, y), icone, subtitulo) in NOS.items():
        ativo = no in ordem
        classe = "no ativo" + (" recusa" if no == "recusar" else "") if ativo else "no"
        sub = resultado_do_no(no, estado) if ativo else subtitulo
        numero = f"<span class='passo'>{ordem[no]}</span>" if ativo and no != "pergunta" else ""
        dica = html.escape(json.dumps({"titulo": no.capitalize(), "funcao": FUNCAO[no], "linhas": detalhes_do_no(no, estado)},
                                      ensure_ascii=False), quote=True)
        cartoes.append(
            f"<div class='{classe}' data-dica=\"{dica}\" style='left:{x - LARGURA / 2}px;top:{y - ALTURA / 2}px'>"
            f"<span class='icone'><i class='ti {icone}'></i></span>"
            f"<span class='textos'><b>{no.capitalize()}</b><small>{html.escape(sub)}</small></span>{numero}</div>")
    return f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
  body {{ margin:0; font-family: "Source Sans Pro", "Segoe UI", system-ui, sans-serif; }}
  #moldura {{ width:760px; height:800px; position:relative; transform-origin: top left; }}
  svg {{ position:absolute; inset:0; overflow:visible; }}
  .seta {{ fill:none; stroke:#cfd5de; stroke-width:1.3; stroke-dasharray:4 5; }}
  .seta.ativa {{ stroke:#2f6db5; stroke-width:2.4; stroke-dasharray:7 6; animation: fluxo 1.2s linear infinite; }}
  .seta.ativa.recusa {{ stroke:#d9480f; }}
  @keyframes fluxo {{ to {{ stroke-dashoffset:-13; }} }}
  @media (prefers-reduced-motion: reduce) {{ .seta.ativa {{ animation:none; }} }}
  .no {{ position:absolute; width:{LARGURA}px; height:{ALTURA}px; box-sizing:border-box; display:flex; align-items:center;
         gap:10px; padding:0 12px; border-radius:12px; background:#f7f8fa; border:1px dashed #d5dae2; color:#a3aab6; }}
  .no .icone {{ width:34px; height:34px; flex:none; border-radius:9px; display:flex; align-items:center; justify-content:center;
                background:#eceff3; font-size:19px; }}
  .no .textos {{ display:flex; flex-direction:column; line-height:1.2; min-width:0; }}
  .no b {{ font-size:14.5px; font-weight:600; }}
  .no small {{ font-size:11.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .no.ativo {{ background:#fff; border:1.5px solid #2f6db5; color:#1f2a44; box-shadow:0 2px 8px rgba(31,64,128,.10); }}
  .no.ativo .icone {{ background:#2f6db5; color:#fff; }}
  .no.ativo small {{ color:#55607a; }}
  .no.ativo.recusa {{ border-color:#d9480f; }}
  .no.ativo.recusa .icone {{ background:#d9480f; }}
  .passo {{ position:absolute; top:-9px; right:-9px; width:22px; height:22px; border-radius:50%; background:#1f2a44; color:#fff;
            font-size:11.5px; font-weight:600; display:flex; align-items:center; justify-content:center; }}
  .no:hover {{ filter:brightness(.97); }}
  #legenda {{ position:absolute; left:0; right:0; bottom:0; display:flex; gap:22px; justify-content:center; font-size:12.5px; color:#55607a; }}
  #legenda span {{ display:flex; align-items:center; gap:6px; }}
  #legenda i.marca {{ width:22px; height:0; border-top:2.4px solid #2f6db5; display:inline-block; }}
  #dica {{ position:absolute; display:none; max-width:430px; background:#1f2a44; color:#fff; font-size:12.5px; line-height:1.45;
           padding:10px 12px; border-radius:8px; pointer-events:none; white-space:pre-wrap; z-index:5;
           box-shadow:0 6px 18px rgba(0,0,0,.18); }}
  #dica b {{ display:block; margin-bottom:4px; font-size:13px; }}
  #dica .funcao {{ color:#c9d4ea; margin-bottom:8px; }}
  #dica .nesta {{ font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; color:#8fa3c8;
                  border-top:1px solid #3a4763; padding-top:6px; margin-bottom:3px; }}
</style>
<div id="moldura">
  <svg viewBox="0 0 760 800" width="760" height="800">
    <defs>
      <marker id="ponta" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M2 1L8 5L2 9" fill="none" stroke="#cfd5de" stroke-width="1.6"/></marker>
      <marker id="ponta-ativa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M2 1L8 5L2 9" fill="none" stroke="#2f6db5" stroke-width="1.8"/></marker>
      <marker id="ponta-recusa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M2 1L8 5L2 9" fill="none" stroke="#d9480f" stroke-width="1.8"/></marker>
    </defs>
    {''.join(setas)}
  </svg>
  {''.join(cartoes)}
  <div id="legenda">
    <span><i class="marca"></i>caminho percorrido, na ordem numerada</span>
    <span><i class="marca" style="border-top:1.3px dashed #cfd5de"></i>não percorrido</span>
    <span><i class="marca" style="border-color:#d9480f"></i>recusa</span>
  </div>
  <div id="dica"></div>
</div>
<script>
  const moldura = document.getElementById('moldura'), dica = document.getElementById('dica');
  function ajustar() {{  // encolhe o desenho se a coluna for mais estreita que 760 px
    const escala = Math.min(1, document.body.clientWidth / 760);
    moldura.style.transform = `scale(${{escala}})`;
    moldura.style.marginLeft = `${{Math.max(0, (document.body.clientWidth - 760 * escala) / 2)}}px`;
  }}
  ajustar(); window.addEventListener('resize', ajustar);
  document.querySelectorAll('.no').forEach(no => {{
    no.addEventListener('mousemove', e => {{
      const d = JSON.parse(no.dataset.dica);
      dica.innerHTML = '';
      const t = document.createElement('b'); t.textContent = d.titulo; dica.appendChild(t);
      const f = document.createElement('div'); f.className = 'funcao'; f.textContent = d.funcao; dica.appendChild(f);
      const n = document.createElement('div'); n.className = 'nesta'; n.textContent = 'nesta pergunta'; dica.appendChild(n);
      dica.appendChild(document.createTextNode(d.linhas.join('\\n')));
      dica.style.display = 'block';
      const r = moldura.getBoundingClientRect(), escala = r.width / 760;
      let x = (e.clientX - r.left) / escala + 16, y = (e.clientY - r.top) / escala + 16;
      if (x + 440 > 760) x = Math.max(4, x - 470);
      if (y + dica.offsetHeight > 800) y = 800 - dica.offsetHeight - 4;
      dica.style.left = x + 'px'; dica.style.top = y + 'px';
    }});
    no.addEventListener('mouseleave', () => dica.style.display = 'none');
  }});
</script>"""


# ── 5. Detalhes técnicos ─────────────────────────────────────────────────────
def mostrar_detalhes(estado):
    interp = estado.get("interpretacao")
    abas = st.tabs(["Pergunta transformada", "Cálculo", "Busca", "Contexto enviado ao modelo", "Conferências"])
    with abas[0]:
        if interp is None:
            st.write("O formulário não passou na validação.")
        else:
            st.json(interp.model_dump(mode="json", exclude_none=True))
    with abas[1]:
        resultado = estado.get("resultado")
        if resultado:
            st.code("\n".join(resultado["rastro"]["código"]), language="python")
            st.dataframe(fluxo.formatar(resultado["tabela"]), use_container_width=True)
            for aviso in resultado["avisos"]:
                st.caption(f"aviso: {aviso}")
        else:
            st.write("Esta pergunta não passou pela consulta.")
    with abas[2]:
        if estado.get("buscas") is not None:
            st.dataframe(estado["buscas"], use_container_width=True, hide_index=True)
            st.dataframe(estado["comentarios"][["grupo", "similaridade", "nota", "estado", "mês", "comentário", "etiquetas"]],
                         use_container_width=True, hide_index=True)
        else:
            st.write("Esta pergunta não passou pela busca.")
    with abas[3]:
        st.code(estado.get("contexto") or "Esta pergunta não chegou à redação.", language=None, wrap_lines=True)
    with abas[4]:
        st.write(f"tentativas de redação: {estado.get('tentativas_redacao', 0)}")
        st.write(f"citações inválidas: {estado.get('citacoes_invalidas') or 'nenhuma'}")
        st.write(f"números fora do contexto: {estado.get('numeros_fora') or 'nenhum'}")
        st.write(f"custo: US$ {custo(estado):.4f}")


# ── 6. A página ──────────────────────────────────────────────────────────────
def escolher_exemplo(pergunta):
    st.session_state["pergunta"] = pergunta
    st.session_state["executar"] = True


with st.sidebar:
    st.subheader("Perguntas de exemplo")
    st.caption("Os exemplos de exploração do enunciado")
    for rotulo, pergunta in PERGUNTAS_EXEMPLO.items():
        st.button(rotulo, on_click=escolher_exemplo, args=(pergunta,), use_container_width=True)
    st.subheader("O que o sistema responde")
    st.markdown(CAPACIDADES)
    st.caption(f"{fluxo.TOTAL:,} avaliações da Olist com comentário, de {fluxo.MES_INICIO} a {fluxo.MES_FIM}".replace(",", "."))

st.title("Tech Challenge 4 - Voz do Cliente")
st.caption("Pedro Henrique Martinez Bertolo · RM373453 · FIAP Pós Tech")

with st.form("formulario"):
    pergunta = st.text_input("Pergunta", key="pergunta", placeholder="Quais os problemas mais apontados sobre entregas?")
    enviada = st.form_submit_button("Perguntar", type="primary")

if (enviada or st.session_state.pop("executar", False)) and st.session_state.get("pergunta", "").strip():
    estado, segundos = executar(st.session_state["pergunta"].strip())
    st.session_state["resultado"] = (estado, segundos)
elif "resultado" in st.session_state:  # interação na página: mostra o resultado guardado, sem rodar de novo
    estado, segundos = st.session_state["resultado"]
    with st.status(resumo_execucao(estado, segundos), state="complete", expanded=False):
        for linha in estado["rastro"]:
            st.markdown(f"**{linha['nó']}** · {linha['o que fez']}")

if "resultado" in st.session_state:
    estado, _ = st.session_state["resultado"]
    st.subheader("Resposta")
    mostrar_resposta(estado)
    st.subheader("Caminho no grafo")
    st.caption("Os nós acesos são as etapas que esta pergunta percorreu, numeradas na ordem; passe o mouse sobre um nó para ver o que ele fez.")
    components.html(desenhar_caminho(estado), height=820)
    with st.expander("Detalhes técnicos"):
        mostrar_detalhes(estado)
