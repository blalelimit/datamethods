import os
import pandas as pd
import pydot

from itertools import combinations
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from PIL import Image
from anytree import Node
from anytree.exporter import DotExporter

from scripts.fpgrowth_tree import *


def onehot_encoder(arr):
    te = TransactionEncoder()
    onehot_df = pd.DataFrame(te.fit_transform(arr), columns=te.columns_)
    print('Length:', len(onehot_df))
    display(onehot_df.head(5))
    return onehot_df


def apriori_fpgrowth_mlxtend(onehot_df, mode, min_support=0.20, min_metric=0.30):
    metric = ''
    # Apiori
    if mode == 'apriori':
        frequent_items = apriori(onehot_df, min_support=min_support, use_colnames=True)
        metric = 'confidence'
        
    # FP Growth
    else:
        frequent_items = fpgrowth(onehot_df, min_support=min_support, use_colnames=True)
        metric = 'lift'
    frequent_items = frequent_items.sort_values(by='support', ascending=False).reset_index(drop=True)
    display(frequent_items.head(5))

    # Association rules
    rules = association_rules(frequent_items, metric=metric, min_threshold=min_metric)
    rules = rules.sort_values(by=['confidence'], ascending=False).reset_index(drop=True)
    print('Shape:', rules.shape)
    display(rules.head(5))
    display(rules.tail(5))


def fpgrowth_python(arr):
    # Remove filepath if exists
    if os.path.exists('outputs/tree.txt'):
        os.remove('outputs/tree.txt')

    # Construct tree from sorted dataset
    tree, _ = constructTree(itemSetList=[sorted(x) for x in arr], frequency=getFrequencyFromList(arr), minSup=0.20)
    tree.display(filepath='outputs/tree.txt')   # Save tree as text file

    # Open tree and read as indented text
    indented_text = ''
    with open('outputs/tree.txt', encoding='utf8') as f:
        indented_text = ''.join(f.readlines()[::-1])

    # Create FP Growth graph
    fpgrowth_graph(indented_text=indented_text)

    
def fpgrowth_graph(indented_text, include_level=True, include_duplicates=True):
    # Add '.' based on level and '*' to duplicate entries
    leaves = indented_text.splitlines()
    if include_level:
        leaves = [x + ' ' + '.' * x.count('\t') for x in leaves]
    if include_duplicates:
        leaves = [leaves[x] + '*' * leaves[:x].count(leaves[x]) for x in range(len(leaves))]

    # Indented text to RenderTree object
    stack = {0: Node(leaves.pop(0))}
    for leaf in leaves:
        leading_spaces = len(leaf) - len(leaf.lstrip('\t'))
        level = int(leading_spaces)
        stack[level] = Node(leaf.strip(), parent=stack[level-1])
    tree = stack[0]

    # Save as dot file
    DotExporter(tree).to_dotfile('outputs/tree.dot')

    # Show tree
    graphs = pydot.graph_from_dot_file('outputs/tree.dot')
    graph = graphs[0]
    graph.set_bgcolor('white')
    # graph.get_node('" Null : 1"')[0].set_shape('box')
    graph.del_node('"\\n"')
    graph.write_png('outputs/tree.png')
    display(Image.open('outputs/tree.png'))