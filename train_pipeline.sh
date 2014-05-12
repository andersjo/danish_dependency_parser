#!/bin/sh
# Switch the direction of the edges
W=working
# Target part-of-speech tag set. The sources files use the DDT tag set.
# To perform the mapping this script looks for a mapping called `da-sto-$TARGET_POS.map` in the `data/pos_map` dir.
TARGET_POS=ddt
MODEL_NAME=ddt

POS_MAP=data/pos_map/da-ddt-$TARGET_POS.map
OPENNLP_BIN=software/apache-opennlp-1.5.2/bin/opennlp
MATE_DIR=software/mate

# Create a new version of the treebank with
#   - direction of modifier switched
#   - original part-of-speech mapped according to POS_MAP file
echo "Rewriting treebank and mapping part of speech"
mkdir -p $W/treebank
for file in data/treebank/*; do
    mod_treebank=$W/$(basename $file)

    # Edge direction
    python src/edge_switch/switch_edges_from_articles.py $file > $mod_treebank.edge

    # Map part-of-speech tags
    python src/map_pos_conll.py $mod_treebank.edge $POS_MAP > $mod_treebank.edge+pos

    # Convert from CONLL06 to CONLL09 format
    python src/conll06_to_09.py $mod_treebank.edge+pos > $mod_treebank
    rm $mod_treebank.edge $mod_treebank.edge+pos

    tagged=$W/$(basename $file)
    tagged=${tagged%.conll}.tagged_tokens
    python src/conll09_to_tagged_tokens.py $mod_treebank > $tagged
done;


# Train and evaluate part-of-speech tagger
echo "Training part-of-speech tagger"
tagger_train=$W/ddt.00-11.tagged_tokens
tagger_test=$W/ddt.12-15.tagged_tokens
tagger_model=model/$MODEL_NAME.pos

$OPENNLP_BIN POSTaggerTrainer -data $tagger_train -lang danish -type maxent -model $tagger_model
$OPENNLP_BIN POSTaggerEvaluator -data $tagger_test -model $tagger_model

# Train and evaluate dependency parser"
echo "Training parser"
parser_model=model/$MODEL_NAME.parse
parser_train=$W/ddt.00-11.conll
parser_test=$W/ddt.12-15.conll

java -Xmx32G -cp $MATE_DIR/anna-3.3.jar is2.parser.Parser -model $parser_model -train $parser_train -test $parser_test -eval $parser_test