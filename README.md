## A trainable part-of-speech tagger and dependency parser for Danish

This package is simply a wrapper that relies on Apache OpenNLP for part-of-speech tagging and mate tools for parsing.

### Usage

Tagging and parsing is performed in a pipeline in which the results of the tagger is feed to the parser. The main script is called `run_danish_pipeline.py`. It takes two parameters: an input text file that has one sentence per line, and an output file name for the results. Note that the input text should be tokenized. The output file is in CONLL9 format.

The tagger and the parser are trained using the `train_danish_pipeline.py` script. For convenience, pre-trained models are included in the `model` directory, and they are automatically used by the run script.  

### Data

The pre-trained models are learned on the training part of the Danish Dependency Treebank. We use the version distributed as a part of the CONLL 2006 shared task on parsing. Part-of-speech tags are converted to the Google universal tagset before training. 

### Included software

* Apache OpenNLP 1.5.2
* Mate tools 3.3
* Universal part-of-speech tags conversion files

### Results

The POS tagger achieves accuracy of 96.8 % on the test portion of the Danish Dependency Treebank using the universal tagset.



