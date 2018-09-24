#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 RARE Technologies <info@rare-technologies.com>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html


"""Callbacks can be used to observe the training process.

Since training in huge corpora can be time consuming, we want to offer the users some insight
into the process, in real time. In this way, convergence issues
or other potential problems can be identified early in the process,
saving precious time and resources.

The metrics exposed through this module can be used to construct Callbacks, which will be called
at specific points in the training process, such as "epoch starts" or "epoch finished".
These metrics can be used to assess mod's convergence or correctness, for example
to save the model, visualize intermediate results, or anything else.

Usage examples
--------------
To implement a Callback, inherit from this base class and override one or more of its methods.

Create a callback to save the training model after each epoch
.. sourcecode:: pycon

    >>> from gensim.test.utils import get_tmpfile
    >>> from gensim.models.callbacks import CallbackAny2Vec
    >>>
    >>>
    >>> class EpochSaver(CallbackAny2Vec):
    ...     '''Callback to save model after each epoch.'''
    ...
    ...     def __init__(self, path_prefix):
    ...         self.path_prefix = path_prefix
    ...         self.epoch = 0
    ...
    ...     def on_epoch_end(self, model):
    ...         output_path = get_tmpfile('{}_epoch{}.model'.format(self.path_prefix, self.epoch))
    ...         model.save(output_path)
    ...         self.epoch += 1
    ...

Create a
"""
