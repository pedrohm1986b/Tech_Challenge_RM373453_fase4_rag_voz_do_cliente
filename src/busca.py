"""Busca de comentários (etapa 5, D-028), reaproveitada pelas ferramentas da etapa 6.

O código é o mesmo do desenv_05, reunido numa classe e com um filtro a mais (todas_etiquetas, desenv_06) para ser importado pelos notebooks
seguintes e pela aplicação. O índice é lido de data/processed/indice_busca/, gerado pelo
desenv_05.
"""

import warnings
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

warnings.filterwarnings("ignore", message=".*langchain-community.*")
from langchain_community.vectorstores import FAISS  # noqa: E402
from langchain_community.vectorstores.utils import DistanceStrategy, maximal_marginal_relevance  # noqa: E402

MODELO_EMBEDDING = "gemini-embedding-2"
DIMENSOES = 768
AJUSTES = {
    "com etiqueta": {"candidatos": 500, "peso": 0.3, "corte": None},
    "sem etiqueta": {"candidatos": 500, "peso": 0.3, "corte": 0.05},
}
PARTES_ETIQUETA = {"sentido": 0, "tema": 1, "detalhe": 2}
COLUNAS_FILTRO = {"nota": "nota", "estado": "estado_cliente", "regiao": "regiao_cliente", "faixa_atraso": "faixa_atraso"}
FILTROS_ACEITOS = ("etiqueta", "todas_etiquetas", "sentido", "tema", "detalhe", "nota", "estado", "regiao", "faixa_atraso", "categoria", "periodo")


class EmbeddingDeBusca(Embeddings):
    """Embedding do Google com o formato de pergunta do gemini-embedding-2."""

    def __init__(self):
        self.modelo = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDING, output_dimensionality=DIMENSOES)

    def embed_documents(self, textos):
        return self.modelo.embed_documents(textos)

    def embed_query(self, pergunta):
        return self.modelo.embed_query(f"task: search result | query: {pergunta}")


def como_lista(valor):
    return list(valor) if isinstance(valor, (list, tuple, set)) else [valor]


def montar_documentos(base, etiquetas):
    """Um documento por comentário, na mesma ordem do índice, com as etiquetas em lista."""
    por_comentario = (etiquetas.query("sem_etiqueta == 0")
                      .assign(etiqueta=lambda d: d["sentido"] + " · " + d["tema"] + " · " + d["detalhe"])
                      .groupby("review_id")["etiqueta"].agg(list))
    documentos = base[["review_id", "nota", "titulo", "texto", "mes_avaliacao", "estado_cliente", "regiao_cliente",
                       "faixa_atraso", "categorias"]].copy()
    documentos["categorias"] = documentos["categorias"].apply(lambda v: list(v) if isinstance(v, (list, np.ndarray)) else [])
    documentos["etiquetas"] = documentos["review_id"].map(por_comentario).apply(lambda v: v if isinstance(v, list) else [])
    return documentos


class BuscaComentarios:
    """Base de comentários, filtros e busca por sentido sobre o índice FAISS."""

    def __init__(self, raiz):
        raiz = Path(raiz)
        load_dotenv(raiz / ".env", override=True)
        processados = raiz / "data" / "processed"
        self.base = pd.read_parquet(processados / "avaliacoes_enriquecidas.parquet")
        self.etiquetas = pd.read_parquet(processados / "etiquetas_base.parquet")
        self.documentos = montar_documentos(self.base, self.etiquetas)
        self.embedding = EmbeddingDeBusca()
        # o arquivo index.pkl é gerado pelo desenv_05, por isso a leitura dele é liberada
        self.loja = FAISS.load_local(str(processados / "indice_busca"), self.embedding,
                                     allow_dangerous_deserialization=True,
                                     distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)
        assert self.loja.index.ntotal == len(self.documentos)

    def permitidos(self, filtros):
        """Posições dos comentários que atendem aos filtros; todas quando não há filtro."""
        documentos = self.documentos
        if not filtros:
            return np.arange(len(documentos))
        desconhecidos = set(filtros) - set(FILTROS_ACEITOS)
        if desconhecidos:
            raise ValueError(f"filtro desconhecido: {sorted(desconhecidos)}")
        permitido = pd.Series(True, index=documentos.index)
        # sentido, tema e detalhe valem juntos dentro da mesma etiqueta
        partes = {campo: como_lista(valor) for campo, valor in filtros.items() if campo in PARTES_ETIQUETA}
        if partes:
            permitido &= documentos["etiquetas"].apply(lambda etiquetas: any(
                all(e.split(" · ")[PARTES_ETIQUETA[campo]] in valores for campo, valores in partes.items())
                for e in etiquetas))
        for campo, valor in filtros.items():
            if campo == "etiqueta":  # ao menos uma das etiquetas
                permitido &= documentos["etiquetas"].apply(lambda etiquetas: any(e in como_lista(valor) for e in etiquetas))
            elif campo == "todas_etiquetas":  # todas as etiquetas no mesmo comentário (padrões)
                permitido &= documentos["etiquetas"].apply(lambda etiquetas: all(e in etiquetas for e in como_lista(valor)))
            elif campo == "categoria":
                permitido &= documentos["categorias"].apply(lambda categorias: any(c in como_lista(valor) for c in categorias))
            elif campo == "periodo":
                inicio, fim = valor
                permitido &= documentos["mes_avaliacao"].between(inicio, fim)
            elif campo in COLUNAS_FILTRO:
                permitido &= documentos[COLUNAS_FILTRO[campo]].isin(como_lista(valor))
        return np.flatnonzero(permitido.to_numpy())

    @staticmethod
    def ajuste_para(filtros):
        """Sem corte quando um filtro de etiqueta garante o assunto; com corte nos demais casos."""
        com_etiqueta = filtros and any(campo in filtros for campo in ("etiqueta", "todas_etiquetas", "tema", "detalhe"))
        return "com etiqueta" if com_etiqueta else "sem etiqueta"

    def buscar(self, pergunta, k=5, filtros=None, diversificar=True):
        """Comentários mais próximos da pergunta, dentro dos filtros, diversificados pela regra da D-028."""
        posicoes = self.permitidos(filtros)
        if len(posicoes) == 0:
            return pd.DataFrame()
        escolha = AJUSTES[self.ajuste_para(filtros)]
        vetor = np.asarray(self.embedding.embed_query(pergunta), dtype="float32")
        parametros = (None if len(posicoes) == len(self.documentos)
                      else faiss.SearchParameters(sel=faiss.IDSelectorBatch(posicoes.astype("int64"))))
        similaridades, ids = self.loja.index.search(vetor[None, :], escolha["candidatos"] if diversificar else k,
                                                    params=parametros)
        validos = ids[0] >= 0
        similaridades, ids = similaridades[0][validos], ids[0][validos]
        if diversificar and escolha["corte"] is not None:
            perto_do_melhor = similaridades >= similaridades[0] - escolha["corte"]
            similaridades, ids = similaridades[perto_do_melhor], ids[perto_do_melhor]
        if diversificar and len(ids) > k:
            escolhidos = maximal_marginal_relevance(vetor, self.loja.index.reconstruct_batch(ids), k=k,
                                                    lambda_mult=escolha["peso"])
            similaridades, ids = similaridades[escolhidos], ids[escolhidos]
        else:
            similaridades, ids = similaridades[:k], ids[:k]
        achados = self.documentos.iloc[ids][["review_id", "nota", "mes_avaliacao", "estado_cliente", "texto",
                                             "etiquetas"]].copy()
        achados.insert(0, "similaridade", similaridades.round(3))
        achados["etiquetas"] = achados["etiquetas"].str.join("; ")
        return (achados.rename(columns={"mes_avaliacao": "mês", "estado_cliente": "estado", "texto": "comentário"})
                .reset_index(drop=True))
