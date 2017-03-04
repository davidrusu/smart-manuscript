#!/usr/bin/python3

"""
    This file is part of Smart Manuscript.

    Smart Manuscript (transcript handwritten notes or inputs)
    Copyright (c) 2017 Daniel Vorberg

    Smart Manuscript is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Smart Manuscript is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Smart Manuscript.  If not, see <http://www.gnu.org/licenses/>.
"""

from inkml_new import InkML, TraceView
from tensorflow.python.platform.app import flags
import numpy as np
import pylab as plt
import os
from corpus import Corpus
from stroke_features import Ink
from utils import Bunch
from copy import deepcopy

__author__ = "Daniel Vorberg"
__copyright__ = "Copyright (c) 2017, Daniel Vorberg"
__license__ = "GPL"


flags.DEFINE_string("iam_on_do_path", "data/IAMonDo-db-1.0",
                    "path to IAMonDo-db-1.0 folder (unzipped)")


class IAMonDo(InkML):

    TEXTLINE = "Textline"
    WORD = "Word"
    TRANSCRIPTION = "transcription"
    TYPE = "type"
    CORRECTION = "Correction"

    @staticmethod
    def condition(element, type_):
        def includes_corrections(element):
            child_include_corrections = any(
                next(child.search(includes_corrections), None) is not None
                for child in element)
            element_is_correction = (
                IAMonDo.TYPE in element.annotation and
                element.annotation[IAMonDo.TYPE] == IAMonDo.CORRECTION)
            return child_include_corrections or element_is_correction

        return (isinstance(element, TraceView) and
                IAMonDo.TYPE in element.annotation and
                element.annotation[IAMonDo.TYPE] == type_ and
                not (next(element.search(includes_corrections), None) is not None))

    def _transformed(self, stroke):
        x_max = self.pagesize[3]
        stroke = deepcopy(stroke)
        for point in stroke:
            point[0] = x_max - point[0]
        return stroke

    def ink(self, trace_refs=None):
        return [self._transformed(stroke)
                for stroke in self._root.ink(trace_refs)]

    def get_segments(self, type_):
        def condition(elem):
            return self.condition(elem, type_)
        for textline in self._root.search(condition):
            yield Bunch(
                transcription=textline.annotation[self.TRANSCRIPTION],
                ink=self.ink(textline._trace_data_refs()))

    @property
    def pagesize(self):

        string = self._root.annotation["Page Bounds"]
        return [float(value) for value in string.split(" ")]

    def plot(self, axes=None, *args, **kwargs):
        if axes is None:
            axes = plt.axes()
        super().plot(axes, *args, **kwargs)
        xmin, ymin, ymax, xmax = self.pagesize
        axes.axis([xmin, xmax, ymin, ymax])


def load(iam_on_db_path):
    corpara_word = []
    corpara_line = []
    for i in range(5):
        word_corpus, line_corpus = _import_set(iam_on_db_path, '%i.set' % i)
        corpara_word.append(word_corpus)
        corpara_line.append(line_corpus)
    return corpara_word, corpara_line


def _import_set(iam_on_db_path, set_filename):
    print("import set: " + iam_on_db_path + "/" + set_filename)

    def files_in_set(path, set_filename):
        with open(path + "/" + set_filename) as f:
            for line in f:
                yield path + "/" + line.rstrip('\n')

    corpara_word = Corpus()
    corpara_line = Corpus()
    num_files = 0
    filenames = list(files_in_set(iam_on_db_path, set_filename))
    for i, inkml_filename in enumerate(filenames):
        print("import {:3}/{:3} ({})  ".format(
            i, len(filenames), inkml_filename), end="\r")
        try:
            num_files += 1
            inkml_file = IAMonDo(inkml_filename)
            for segment in inkml_file.get_segments(IAMonDo.WORD):
                corpara_word.append((segment.transcription, Ink(segment.ink)))
            for segment in inkml_file.get_segments(IAMonDo.TEXTLINE):
                corpara_line.append((segment.transcription, Ink(segment.ink)))
        except FileNotFoundError:
            print("file {} not found {:20}".format(inkml_filename, ""))
            pass
        if i==10:
            break

    print(" {} words and {} textlines have been imported "
          "from {} inkml-files ".format(len(corpara_word), len(corpara_line),
                                        num_files))

    return corpara_word, corpara_line


def main():
    """ load the full IAMonDo database and show random lines and transcription
    """

    words, lines = _import_set(flags.FLAGS.iam_on_do_path, "0.set")
    while True:
        lines.plot_sample()


if __name__ == "__main__":
    main()
