"""
Description     : Simple Python implementation of the Apriori Algorithm
Usage:
    $python apriori.py -f DATASET.csv -s minSupport  -c minConfidence
    $python apriori.py -f DATASET.csv -s 0.15 -c 0.6
"""

import sys

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser


def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """calculates the support for items in the itemSet and returns a subset
       of the itemSet each of whose elements satisfies the minimum support"""
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in localSet.items():
                support = (float(count)/len(transactionList)) * 100

                if support >= minSupport * 100:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return (float(freqSet[item])/len(transactionList)) * 100

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in largeSet.items()[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = (getSupport(item)/getSupport(element)) * 100
                    if confidence >= minConfidence * 100:
                        lift = getSupport(item) / (getSupport(element) * getSupport(item - element)) * 100
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           getSupport(item), confidence, lift))
    return toRetItems, toRetRules


def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    # for item, support in sorted(items, key=lambda (item, support): support):
        # print "item: %s , %.3f" % (str(item), support)
    # print "\n------------------------ RULES:"
    # for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
        # pre, post = rule
        # print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)
    for rule, support, confidence, lift in sorted(rules, key=lambda(rule, support, confidence, lift): support):
        pre, post = rule
        # print "Rule: %-40s ==> %-40s  Sup: %.2f%%   Conf: %.2f%%" % (str(pre), str(post), support, confidence)
        yield pre, post, support, confidence, lift

def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        """
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = frozenset(line.split(','))
                yield record
        """
        with open(fname, 'rU') as f:
            datas = csv.reader(f)
            for data in datas:
                for count in range(data.count('')):
                    data.remove('')
                yield frozenset(data)

if __name__ == "__main__":
    import csv
    optparser = OptionParser()
    optparser.add_option('-f', '--inputFile',
                         dest='input',
                         help='filename containing csv',
                         default=None)
    optparser.add_option('-s', '--minSupport',
                         dest='minS',
                         help='minimum support value',
                         default=0.15,
                         type='float')
    optparser.add_option('-c', '--minConfidence',
                         dest='minC',
                         help='minimum confidence value',
                         default=0.6,
                         type='float')

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
            inFile = sys.stdin
    elif options.input is not None:
            inFile = dataFromFile(options.input)
    else:
            print 'No dataset filename specified, system with exit\n'
            sys.exit('System will exit')

    minSupport = options.minS
    minConfidence = options.minC

    items, rules = runApriori(inFile, minSupport, minConfidence)

    printResults(items, rules)
    
    with open('/Users/lipenghao/Desktop/Apriori-master/support=20%,confidence=30%to90%/support=20%,confidence=90%.csv', 'w') as f:
        data = csv.writer(f)
        header = ['Item1', 'Item2', 'Support', 'Confidence', 'Lift']
        data.writerow(header)
        for pre, post, support, confidence, lift in printResults(items, rules):
            temp = list()
            temp.append(pre)
            temp.append(post)
            temp.append("%.2f%%" % support)
            temp.append("%.2f%%" % confidence)
            temp.append("%.3f" % lift)
            data.writerow(temp)
    
