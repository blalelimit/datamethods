# Sources:
# https://github.com/chonyy/fpgrowth_py
import textwrap

from csv import reader
from collections import defaultdict
from itertools import chain, combinations


def indent(amount, text='', ch=' '):
    return textwrap.indent(text, amount * ch)


class Nodes:
    def __init__(self, itemName, frequency, parentNodes):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNodes
        self.children = {}
        self.next = None
        self.indented = ''


    def increment(self, frequency):
        self.count += frequency


    def display(self, ind=1, filepath='tree.txt'):
        with open(filepath, 'a') as f:
            print('\t' * (ind-1), self.itemName, ' : ', self.count, sep='', file=f)
            for child in list(self.children.values()):
                child.display(ind+1, filepath)


def constructTree(itemSetList, frequency, minSup):
    headerTable = defaultdict(int)
    # Counting frequency and create header table
    for index, itemSet in enumerate(itemSetList):
        for item in itemSet:
            headerTable[item] += frequency[index]

    # Deleting items lower than minimum support
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    if len(headerTable) == 0:
        return None, None

    # HeaderTable column [Item: [frequency, headNodes]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]

    # Initialize Null node
    fpTree = Nodes('Null', 1, None)

    # Update FP tree for each cleaned and sorted itemSet
    for index, itemSet in enumerate(itemSetList):
        itemSet = [item for item in itemSet if item in headerTable]
        itemSet.sort(key=lambda item: headerTable[item][0], reverse=True)

        # Traverse from root to leaf, update tree with given item
        currentNodes = fpTree
        for item in itemSet:
            currentNodes = updateTree(item, currentNodes, headerTable, frequency[index])

    return fpTree, headerTable

def updateHeaderTable(item, targetNodes, headerTable):
    if headerTable[item][1] == None:
        headerTable[item][1] = targetNodes
    else:
        currentNodes = headerTable[item][1]

        # Traverse to the last Nodes then link it to the target
        while currentNodes.next != None:
            currentNodes = currentNodes.next
        currentNodes.next = targetNodes


def updateTree(item, treeNodes, headerTable, frequency):
    # If the item already exists, increment the count
    if item in treeNodes.children:
        treeNodes.children[item].increment(frequency)
    else:
        # Create a new branch
        newItemNodes = Nodes(item, frequency, treeNodes)
        treeNodes.children[item] = newItemNodes
        # Link the new branch to header table
        updateHeaderTable(item, newItemNodes, headerTable)

    return treeNodes.children[item]


def ascendFPtree(Nodes, prefixPath):
    if Nodes.parent != None:
        prefixPath.append(Nodes.itemName)
        ascendFPtree(Nodes.parent, prefixPath)


def findPrefixPath(basePat, headerTable):
    # First Nodes in linked list
    treeNodes = headerTable[basePat][1] 
    condPats = []
    frequency = []
    while treeNodes != None:
        prefixPath = []
        # From leaf Nodes all the way to root
        ascendFPtree(treeNodes, prefixPath)  
        if len(prefixPath) > 1:
            # Storing the prefix path and it's corresponding count
            condPats.append(prefixPath[1:])
            frequency.append(treeNodes.count)

        # Go to next Nodes
        treeNodes = treeNodes.next  

    return condPats, frequency


def mineTree(headerTable, minSup, preFix, freqItemList):
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][0])] 
    # Start with the lowest frequency
    for item in sortedItemList:  
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup) 
        if newHeaderTable != None:
            # Mining recursively on the tree
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList)


def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))


def getSupport(testSet, itemSetList):
    count = 0
    for itemSet in itemSetList:
        if set(testSet).issubset(itemSet):
            count += 1
    return count


def associationRule(freqItemSet, itemSetList, minConf):
    rules = []
    for itemSet in freqItemSet:
        subsets = powerset(itemSet)
        itemSetSup = getSupport(itemSet, itemSetList)
        for s in subsets:
            confidence = float(itemSetSup / getSupport(s, itemSetList))
            if(confidence > minConf):
                rules.append([set(s), set(itemSet.difference(s)), confidence])
    return rules


def getFrequencyFromList(itemSetList):
    frequency = [1 for _ in range(len(itemSetList))]
    return frequency


def fpgrowth_tree(itemSetList, minSupRatio, minConf):
    frequency = getFrequencyFromList(itemSetList)
    minSup = len(itemSetList) * minSupRatio
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    if fpTree == None:
        print('No frequent item set')
    else:
        freqItems = []
        mineTree(headerTable, minSup, set(), freqItems)
        rules = associationRule(freqItems, itemSetList, minConf)
        return freqItems, rules