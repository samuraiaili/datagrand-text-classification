# _*_ coding: utf-8 _*_

"""
Train distributed representation of words using gensim.

Author: StrongXGP
Date:	2018/07/13
"""

import gc
from gensim.models.word2vec import Word2Vec


def load_word_samples(train_data_file, test_data_file):
    """Load training and testing data, get the words of each sample in two dataset and return."""
    train_lines = open(train_data_file, 'r', encoding='utf-8').read().splitlines()[1:]
    test_lines = open(test_data_file, 'r', encoding='utf-8').read().splitlines()[1:]

    train_word_samples = [line.split(',')[2] for line in train_lines]
    test_word_samples = [line.split(',')[2] for line in test_lines]
    word_samples = train_word_samples + test_word_samples

    word_samples = [word_sample.split() for word_sample in word_samples]

    return word_samples


def batch_iter(data, batch_size=5000):
    """Generate batch iterator."""
    data_size = len(data)
    num_batches = ((data_size - 1) // batch_size) + 1
    for batch_num in range(num_batches):
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1) * batch_size, data_size)
        yield data[start_index:end_index]


if __name__ == '__main__':
    # Load data
    # =========================================================================

    print("Loading data...")

    train_data_file = "../../raw_data/train_set.csv"
    test_data_file = "../../raw_data/test_set.csv"
    sentences = load_word_samples(train_data_file, test_data_file)

    # Calculate the size of vocabulary
    # =========================================================================

    words = []
    for sentence in sentences:
        words.extend(sentence)
    print("The total number of words is: %d" % len(set(words)))

    del words
    gc.collect()

    # Train and save word2vec model
    # =========================================================================

    print("Start training...")

    model = Word2Vec(size=300, min_count=5)
    model.build_vocab(sentences)
    print(model)

    batches = batch_iter(sentences, batch_size=20000)
    for batch in batches:
        model.train(batch, total_examples=model.corpus_count, epochs=model.epochs)

    print("Training Finish! ^_^")

    model.wv.save("datagrand-word-300d.bin")
    model.wv.save_word2vec_format("datagrand-word-300d.txt", binary=False)