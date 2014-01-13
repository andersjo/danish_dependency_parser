import os
from os.path import join

SOFTWARE_DIR = join(os.path.dirname(__file__), 'software')
DATA_DIR = join(os.path.dirname(__file__), 'data')
MODEL_DIR = join(os.path.dirname(__file__), 'model')

MATE_DIR = join(SOFTWARE_DIR, 'mate')
OPENNLP_DIR = join(SOFTWARE_DIR, 'apache-opennlp-1.5.2')
OPENNLP_BIN = reduce(join, [OPENNLP_DIR, 'bin', 'opennlp'])
OPENNLP_TOOL_JAR = reduce(join, [OPENNLP_DIR, 'lib', 'opennlp-tools-1.5.2-incubating.jar'])

POS_TAG_MODEL = join(MODEL_DIR, 'ddt-universal.pos')
PARSE_MODEL = join(MODEL_DIR, 'ddt-universal.parse')