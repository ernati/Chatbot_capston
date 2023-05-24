from haystack.pipelines import Pipeline
from haystack.utils import launch_es
import time
from ela.es_classes import ESdocumentstore_plus_retriever as ES
from ela.es_classes import InMemorydocumentstore_plus_retriever as IM
# from ela.es_classes import Readers
from soynlp.normalizer import *
from ela.app_alpaka import koalpaca


class Chatbot() :
    def __init__(self,check):
        #launch es
        self.start_es()

        ##initialize variables
        self._es = ES()
        # self._document_store_for_faq = IM()
        self._document_store_for_embedding = IM()
        self._koalpaca = koalpaca()
        # self._readers = Readers()

        self._check = check

        ##setting chatbot
        # self.add_faq_to_faqstore()
        self.add_documents_to_es()

    ##chatbot methods
    def start_es(self):
        launch_es()
        time.sleep(30)

    # def add_faq_to_faqstore(self):
    #     self._document_store_for_faq.add_faq()
    #     return

    def add_documents_to_es(self):
        self._es.add_documents(self._check)

    def Chatbot_pipeline(self, query : str):
        # # 1. faq use doctoanswers
        # first_pipeline = Pipeline()
        # first_pipeline.add_node(component=self._document_store_for_faq.get_embedding_retriever(), name="Retriever",
        #                         inputs=["Query"])
        # first_pipeline.add_node(component=self._document_store_for_faq.get_doc_to_answers(), name="Docs2Answers",
        #                         inputs=["Retriever"])
        #
        # result_faq = first_pipeline.run(query=query, params={"Retriever": {"top_k": 10}})
        #
        # if result_faq['answers'] and result_faq["answers"][0].score >= boundscore:
        #     # return answer
        #     for num in range(0, len(result_faq['answers'])) :
        #         result_faq['answers'][num].answer = repeat_normalize(result_faq['answers'][num].answer, num_repeats=1)
        #
        #     return result_faq


        # else:  # score < boundscore

        document_list = []
        answer = []

        # 1_new. first BM25
        result_BM25 = self._es.get_BM25retriever().retrieve(query=query, top_k=15)

        # if BM25 don't get any documents
        if len(result_BM25)==0 :
            answer.append( self._koalpaca.ask(query, []) )
            return answer

        # 2_new. use embedding retriever by using documents from BM25
        self._document_store_for_embedding.get_document_store().delete_documents()
        self._document_store_for_embedding.get_document_store().write_documents(result_BM25)
        self._document_store_for_embedding.get_document_store().update_embeddings(self._document_store_for_embedding.get_embedding_retriever())
        result_embedding_retriever = self._document_store_for_embedding.get_embedding_retriever().retrieve(query=query,top_k=5)

        document_list.extend(result_embedding_retriever)

        # result = []

        for Document in document_list :
            answer.append( self._koalpaca.ask( query, Document['content'] ) )

        # result_reader = self._readers.get_FReader().predict(query=query, documents=document_list, top_k=9)

        # ##sonlyp
        # for num in range(0, len(result_reader['answers'])):
        #     result_reader['answers'][num].answer = repeat_normalize(result_reader['answers'][num].answer, num_repeats=1)
        #
        # return result_reader


        # return result
        return answer

    ## get methods
    def get_es(self):
        return self._es

    # def get_document_store_for_faq(self):
    #     return self._document_store_for_faq

    def get_document_store_for_embedding(self):
        return self._document_store_for_embedding

    # def get_reader(self):
        # self._readers = Readers()