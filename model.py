"""
TFIDF + SGD Model for text classification
"""

import json

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier


class LabelMapStep(object):
    """Label Map Step"""

    def __init__(self, data_dir):
        super(LabelMapStep, self).__init__()

        self.data_dir = data_dir

    def train(self, labels):
        '''Create the label map from the set of training examples
        '''

        unique_labels = list(set(labels))

        label_map = {
            "forward": {},
            "backward": {}
        }

        for idx, label in enumerate(unique_labels):
            label_map['forward'][label] = idx
            label_map['backward'][idx] = label

        with open(self.data_dir + 'label_map.json', 'w') as label_map_file:
            json.dump(label_map, label_map_file)

        self.label_map = label_map

        return label_map

    def process(self, labels):
        '''Use the label map to change the labels to their indexes
        '''

        if not self.label_map:
            with open(self.data_dir + 'label_map.json', 'r') as label_map_file:
                self.label_map = json.load(label_map_file)

        return [self.label_map['forward'][label] for label in labels]

    def format_predictions(self, predictions, classes):

        formatted_predictions = []

        for prediction in predictions:

            formatted_prediction = {}

            for idx, probability in enumerate(prediction):
                class_id = classes[idx]
                class_name = self.label_map['backward'][class_id]
                formatted_prediction[class_name] = probability

            formatted_predictions.append(formatted_prediction)

        return formatted_predictions


class PresearcherModel(object):
    """TFIDF + SGD Model for text classification"""

    def __init__(self, data_dir):
        super(PresearcherModel, self).__init__()

        self.data_dir = data_dir
        self.embedder = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                        stop_words='english',
                                        ngram_range=[1, 2],
                                        strip_accents='unicode')
        self.label_mapper = LabelMapStep(data_dir=self.data_dir)
        self.classifier = SGDClassifier(loss="log")

    def extract_fields(self, examples):
        ''' Extract relevant fields from content objects
        '''

        return [example.get('title', '') + ' ' +
                example.get('description', '') for
                example in examples]

    def train(self, training_data):

        samples = self.extract_fields(
                    [example['content'] for example in training_data])
        labels = [example['label'] for example in training_data]

        self.embedder.fit(samples)
        embeddings = self.embedder.transform(samples)

        self.selector = SelectKBest(f_classif, k=min(20000, embeddings.shape[1]))
        self.selector.fit(embeddings, labels)
        selected_embeddings = self.selector.transform(embeddings).astype('float32')

        self.label_map = self.label_mapper.train(labels)
        label_indexes = self.label_mapper.process(labels)

        self.classifier.fit(selected_embeddings, label_indexes)

    def predict(self, samples):

        samples = self.extract_fields(samples)

        # TODO Pre-check that we are ready
        embeddings = self.embedder.transform(samples)

        selected_embeddings = self.selector.transform(embeddings).astype('float32')
        predictions = self.classifier.predict_proba(selected_embeddings)

        classes = self.classifier.classes_
        formatted = self.label_mapper.format_predictions(predictions, classes)

        return formatted
