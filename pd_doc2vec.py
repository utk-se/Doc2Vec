import re
import gensim
from gensim.models.doc2vec import TaggedDocument
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class doc2vec:

    def __init__(self, df, X, Y, build=False):
        self.w = re.compile("\w+", re.I)
        if 'basestring' not in globals():
            basestring = str

        # Hyperparameters : https://arxiv.org/pdf/1607.05368.pdf
        self.vector_size = 300
        self.window_size = 15
        self.min_count = 2
        self.sampling_threshold = 1e-4
        self.negative_size = 5
        self.train_epoch = 50
        self.dm = 0
        self.worker_count = 7


        labeled_sentences = []
        df_tags = []

        if isinstance(Y, basestring):
            df_tags.append(Y)
        if isinstance(Y, list):
            df_tags = Y
        elif not isinstance(Y, list):
            raise TypeError
        self.df = df
#         print(self.df)
        self.x = X
        self.y = Y
        self.df_tags = df_tags
        self.testseries = df[df_tags[0]].unique()
        self.testseries_name = df_tags[0]
        if build == True:
            for index, datapoint in df.iterrows():
                tokenized_words = re.findall(self.w, datapoint[X].lower())
                labeled_sentences.append(TaggedDocument(words=tokenized_words, tags=[datapoint[i] for i in df_tags]))
            model = gensim.models.doc2vec.Doc2Vec(vector_size=self.vector_size,
                                                  window_size=self.window_size,
                                                  min_count=self.min_count,
                                                  sampling_threshold=self.sampling_threshold,
                                                  negative_size=self.negative_size,
                                                  train_epoch=self.train_epoch,
                                                  dm=self.dm,
                                                  worker_count=self.worker_count)
            model.build_vocab(labeled_sentences)
            model.train(labeled_sentences, total_examples=model.corpus_count, epochs=model.epochs)
            self.model = model

    def score(self, verbose=False):

        df = self.df
        X = self.x
        Y =self.y
        self.verbose = verbose
        if 'basestring' not in globals():
            basestring = str

        labeled_sentences = []
        df_tags = []

        if isinstance(Y, basestring):
            df_tags.append(Y)
        if isinstance(Y, list):
            df_tags = Y
        elif not isinstance(Y, list):
            raise TypeError
       


        if verbose:
            print("splitting train and test")
        train, test = train_test_split(self.df, shuffle=True, test_size=0.05)

        if verbose:
            print("labeling sentences")
        for index, datapoint in train.iterrows():
            tokenized_words = re.findall(self.w, datapoint[X].lower())
            labeled_sentences.append(TaggedDocument(words=tokenized_words, tags=[datapoint[i] for i in df_tags]))

        model = gensim.models.doc2vec.Doc2Vec(vector_size=self.vector_size,
                                              window_size=self.window_size,
                                              min_count=self.min_count,
                                              sampling_threshold=self.sampling_threshold,
                                              negative_size=self.negative_size,
                                              train_epoch=self.train_epoch,
                                              dm=self.dm,
                                              worker_count=self.worker_count)
        if verbose:
            print("training model")
        model.build_vocab(labeled_sentences)
        model.train(labeled_sentences, total_examples=model.corpus_count, epochs=model.epochs)
        self.model = model

        if verbose:
            print("making predictions")
        test['results'] = self.predict(test[X])
        if verbose:
            print("Scoring results")
        print("Label Score: ")
        labelaccuracy = f1_score(test[self.testseries_name], test['results'], average=None)
        print(labelaccuracy)  # Uses train test split to get score
        print("Accuracy Score: ")
        accuracy = accuracy_score(test[self.testseries_name], test['results'])
        print(accuracy)        # Uses train test split to get score
        return [labelaccuracy, accuracy]


    def predict_taggedtext(self,
                           document):  # takes in a taged document and infers vector and returns whether it is releveant or not (1 or 0)
        inferred_vector = document
        inferred_vector = self.model.infer_vector(inferred_vector)
        sims = self.model.docvecs.most_similar([inferred_vector], topn=len(self.model.docvecs))
        return sims

    def predict_text(self, document):  # takes in a string and infers vector and returns vectors and distance
        tokenized_words = re.findall(self.w, document.lower())
        inferred_vector = TaggedDocument(words=tokenized_words, tags=["inferred_vector"])[0]
        inferred_vector = self.model.infer_vector(inferred_vector)
        sims = self.model.docvecs.most_similar([inferred_vector], topn=len(self.model.docvecs))
        tags = []
        for col in self.df_tags:
            tags.append([rec for rec in sims if rec[0] in set(self.df[col].unique())][0][0])
        return tags
    
    def predict_sims(self, document):  # takes in a string and infers vector and returns vectors and distance
        tokenized_words = re.findall(self.w, document.lower())
        inferred_vector = TaggedDocument(words=tokenized_words, tags=["inferred_vector"])[0]
        inferred_vector = self.model.infer_vector(inferred_vector)
        sims = self.model.docvecs.most_similar([inferred_vector], topn=len(self.model.docvecs))
        return sims
    
    def get_vector(self, document):  # takes in a string and infers vector and returns vectors and distance
        tokenized_words = re.findall(self.w, document.lower())
        inferred_vector = TaggedDocument(words=tokenized_words, tags=["inferred_vector"])[0]
        inferred_vector = self.model.infer_vector(inferred_vector)
        return inferred_vector

    def predict_text_main(self, document, col=None):  # takes in a string and infers vector and returns vectors and distance
        if col == None:
            col = self.df_tags[0]
        tokenized_words = re.findall(self.w, document.lower())
        inferred_vector = TaggedDocument(words=tokenized_words, tags=["inferred_vector"])[0]
        inferred_vector = self.model.infer_vector(inferred_vector)
        sims = self.model.docvecs.most_similar([inferred_vector], topn=len(self.model.docvecs))
#         print([rec for rec in sims if rec[0] in set(self.df[self.df_tags[0]].unique())])
        return [rec for rec in sims if rec[0] in set(self.df[col].unique())][0][0]



    def label_sentences(self, df, X, Y):
        # trick for py2/3 compatibility
        if 'basestring' not in globals():
            basestring = str

        labeled_sentences = []
        df_tags = []

        if isinstance(Y, basestring):
            df_tags.append(Y)
        if isinstance(Y, list):
            df_tags = Y
        elif not isinstance(Y, list):
            raise TypeError
        self.df = df
        self.x = X
        self.y = Y

        for index, datapoint in df.iterrows():
            tokenized_words = re.findall(self.w, datapoint[X].lower())
            labeled_sentences.append(TaggedDocument(words=tokenized_words, tags=[datapoint[i] for i in df_tags]))
        return labeled_sentences

    def predict(self, X):  # Takes a series of text and returns a series of predictions
        if self.verbose:
            from tqdm import tqdm
            tqdm.pandas()
            return X.progress_apply(self.predict_text_main)
        else:
            return X.apply(self.predict_text_main)



