import os
from haystack.document_stores import ElasticsearchDocumentStore,InMemoryDocumentStore
from haystack.nodes import BM25Retriever,EmbeddingRetriever
from haystack.nodes.other.docs2answers import Docs2Answers
import pandas as pd
from haystack.nodes import FARMReader
from haystack.pipelines import TextIndexingPipeline
import json

with open(os.path.join( "chatbot_config.json" )) as f:
    config = json.load(f)

class ESdocumentstore_plus_retriever :
    def __init__(self):
        self._document_store = ElasticsearchDocumentStore(
        host="127.0.0.1",
        username="",
        password="",
        index="document",
        similarity="cosine",
        )
        self._BM25retriever =  BM25Retriever(document_store=self._document_store)
        self._embedding_retriever = EmbeddingRetriever(
        document_store=self._document_store,
        embedding_model=config["sentence_embedding_model"],
        use_gpu=True,
        scale_score=False,
        )

    def get_document_store(self):
        return self._document_store

    def get_BM25retriever(self):
        return self._BM25retriever

    def get_embedding_retriever(self):
        return self._embedding_retriever

    def add_documents(self,check : int):
        self._document_store.delete_documents()
        outputfile_heejung = os.path.join( config["data_path"], config["wiki_path"] )
        files_to_index_heejung = []

        ##all file
        if(check) :
            for dir in os.listdir(outputfile_heejung) :
                a = os.path.join(outputfile_heejung, dir)
                for dirdir in os.listdir(a) :
                    files_to_index_heejung.append(os.path.join(a, dirdir ))

        else :
            # test part of files
            a = os.path.join(outputfile_heejung, "AA", "")
            for dirdir in os.listdir(a):
                files_to_index_heejung.append(os.path.join(a, dirdir))

            a = os.path.join(outputfile_heejung, "AC", "")
            for dirdir in os.listdir(a):
                files_to_index_heejung.append(os.path.join(a, dirdir))

        indexing_pipeline = TextIndexingPipeline(self._document_store)
        indexing_pipeline.run_batch(file_paths=files_to_index_heejung)


class InMemorydocumentstore_plus_retriever :
    def __init__(self):
        self._document_store = InMemoryDocumentStore(use_bm25=True, embedding_dim=768)
        self._embedding_retriever = EmbeddingRetriever(
        document_store=self._document_store,
        embedding_model=config["sentence_embedding_model"],
        use_gpu=True,
        scale_score=False,
        )
        # self._doc_to_answers = Docs2Answers()

    def get_document_store(self):
        return self._document_store

    def get_embedding_retriever(self):
        return self._embedding_retriever

    # def get_doc_to_answers(self):
    #     return self._doc_to_answers

    # def add_faq(self):
    #     df = pd.read_csv(os.path.join(config["data_path"], config["faq_path"], "question_answer.csv"))
    #     df.fillna(value="", inplace=True)
    #     df["question"] = df["question"].apply(lambda x: x.strip())
    #
    #     questions = list(df["question"].values)
    #     df["question_emb"] = self._embedding_retriever.embed_queries(queries=questions).tolist()
    #     df = df.rename(columns={"question": "content"})
    #
    #     docs_to_index = df.to_dict(orient="records")
    #     self._document_store.write_documents(docs_to_index)
    #     self._document_store.update_embeddings( self._embedding_retriever )

# class Readers :
#     def __init__(self):
#         self._FReader = FARMReader( model_name_or_path = config["qa_model"], use_gpu=True )
#     def get_FReader(self):
#         return self._FReader
