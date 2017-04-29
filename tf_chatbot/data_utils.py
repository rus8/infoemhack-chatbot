# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utilities for downloading data from WMT, tokenizing, vocabularies."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

from six.moves import urllib

from tensorflow.python.platform import gfile

# Special vocabulary symbols - we always put them at the start.
_PAD = "_PAD"
_GO = "_GO"
_EOS = "_EOS"
_UNK = "_UNK"
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

# Regular expressions used to tokenize.
_WORD_SPLIT = re.compile("([.,!?\"':;)(])")
_DIGIT_RE = re.compile(r"\d")

replaces = {"n\'t": " not", "\'ll": " will", "\'re": " are", " he\'s": " he is", " she\'s": " she is", " it\'s": " it is", " there\'s": " there is",
            "\'em": " them", "i\'m": "i am", " who\'s": " who is", " what\'s": " what is", " that\'s": " that is"}

def basic_tokenizer(sentence):
    """Very basic tokenizer: split the sentence into a list of tokens."""

    strr = sentence.lower()
    for key, value in replaces.items():
        # print(key)
        if key in strr:
            strr = strr.replace(key, value)

    words = []
    for space_separated_fragment in strr.strip().split():
        words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
    return [w for w in words if w]


def create_vocabulary(vocabulary_path, data_path, at_data, max_vocabulary_size,
                      tokenizer=None, normalize_digits=True):

    if not gfile.Exists(vocabulary_path):
        print("Creating vocabulary %s from %s and %s" % (vocabulary_path, at_data, data_path))
        vocab = {}
        with gfile.GFile(at_data, mode="r") as f:
            counter = 0
            for line in f:
                counter += 1
                if counter % 5000 == 0:
                    print("  processing line %d" % counter)
                # line = line.encode('utf-8')
                if tokenizer  is not None:
                    tokens = tokenizer(line)
                else:
                    tokens = basic_tokenizer(line)
                for w in tokens:
                    word = re.sub(_DIGIT_RE, "0", w) if normalize_digits else w
                    if word in vocab:
                        vocab[word] += 1
                    else:
                        vocab[word] = 1
            vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
            vocab = {}
        with gfile.GFile(data_path, mode="r") as f:
            counter = 0
            for line in f:
                counter += 1
                if counter % 5000 == 0:
                    print("  processing line %d" % counter)
                # line = line.encode('utf-8')
                if tokenizer is not None:
                    tokens = tokenizer(line)
                else:
                    tokens = basic_tokenizer(line)
                for w in tokens:
                    word = re.sub(_DIGIT_RE, "0", w) if normalize_digits else w
                    if word in vocab:
                        vocab[word] += 1
                    else:
                        vocab[word] = 1
            aug_vocab_list = sorted(vocab, key=vocab.get, reverse=True)
            for word in aug_vocab_list:
                if word in vocab_list:
                    continue
                else:
                    vocab_list.append(word)
            print('>> Full Vocabulary Size :',len(vocab_list))
            if len(vocab_list) > max_vocabulary_size:
                vocab_list = vocab_list[:max_vocabulary_size]
            with gfile.GFile(vocabulary_path, mode="w") as vocab_file:
                for w in vocab_list:
                    vocab_file.write(w + "\n")


def initialize_vocabulary(vocabulary_path):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    vocabulary_path = os.path.join(cur_dir, vocabulary_path)
    if gfile.Exists(vocabulary_path):
        rev_vocab = []
        with gfile.GFile(vocabulary_path, mode="r") as f:
            rev_vocab.extend(f.readlines())
        rev_vocab = [line.strip() for line in rev_vocab]
        vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
        return vocab, rev_vocab
    else:
        raise ValueError("Vocabulary file %s not found.", vocabulary_path)


def sentence_to_token_ids(sentence, vocabulary, tokenizer=None, normalize_digits=True):

    if tokenizer is not None:
        words = tokenizer(sentence)
    else:
        words = basic_tokenizer(sentence)
    if not normalize_digits:
        return [vocabulary.get(w, UNK_ID) for w in words]
    # Normalize digits by 0 before looking words up in the vocabulary.
    return [vocabulary.get(re.sub(_DIGIT_RE, "0", w), UNK_ID) for w in words]


def data_to_token_ids(data_path, target_path, vocabulary_path,
                      tokenizer=None, normalize_digits=True):

    if not gfile.Exists(target_path):
        print("Tokenizing data in %s" % data_path)
        vocab, _ = initialize_vocabulary(vocabulary_path)
        with gfile.GFile(data_path, mode="r") as data_file:
            with gfile.GFile(target_path, mode="w") as tokens_file:
                counter = 0
                for line in data_file:
                    # line = line.encode('utf-8')
                    counter += 1
                    if counter % 5000 == 0:
                        print("  tokenizing line %d" % counter)
                    token_ids = sentence_to_token_ids(line, vocab, tokenizer,
                                                      normalize_digits)
                    tokens_file.write(" ".join([str(tok) for tok in token_ids]) + "\n")



def prepare_custom_data(working_directory, phrases, at_phrases, train_enc, train_dec, test_enc, test_dec, vocabulary_size, tokenizer=None):

    # Create vocabularies of the appropriate sizes.
    vocab_path = os.path.join(working_directory, "joint%d.voc" % vocabulary_size)
    create_vocabulary(vocab_path, phrases, at_phrases, vocabulary_size, tokenizer)

    # Create token ids for the training data.
    enc_train_ids_path = train_enc + (".ids%d" % vocabulary_size)
    dec_train_ids_path = train_dec + (".ids%d" % vocabulary_size)
    data_to_token_ids(train_enc, enc_train_ids_path, vocab_path, tokenizer)
    data_to_token_ids(train_dec, dec_train_ids_path, vocab_path, tokenizer)

    # Create token ids for the development data.
    enc_dev_ids_path = test_enc + (".ids%d" % vocabulary_size)
    dec_dev_ids_path = test_dec + (".ids%d" % vocabulary_size)
    data_to_token_ids(test_enc, enc_dev_ids_path, vocab_path, tokenizer)
    data_to_token_ids(test_dec, dec_dev_ids_path, vocab_path, tokenizer)

    return (enc_train_ids_path, dec_train_ids_path, enc_dev_ids_path, dec_dev_ids_path, vocab_path)