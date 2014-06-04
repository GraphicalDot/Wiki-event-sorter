from nltk.tree import Tree
import copy

##https://github.com/eventdata/PETRARCH/blob/master/petrarch/utilities.py
def coref_replace(event_dict, key):
    """
    Function to replace pronouns with the referenced noun phrase. Iterates
    over each sentence in a news story and pulls coreference information
    from the applicable sentence, even if it is from another sentence. Also
    keeps track of any changes in indexes made by replacing pronouns, i.e.,
    the reference is longer than the reference so the tree index changes for
    future references. Filters coreferences on various dimensions to ensure
    only "good" coreferences are replaced. The default behavior is to do
    no replacement rather than a bad replacement. The function does not
    return a value, instead the event_dict is updated with the new parse tree
    containing the coref information.

    Parameters
    ----------

    event_dict: Dictionary.
                    Dictionary of sentence information, such as produced by
                    utilities.parse_sents().

    key: String.
            ID of the event or news story being processed.

    """
    #TODO: This could use some major refactoring.
    if 'coref_info' in event_dict[key]['sent_info'].keys():
        sent_info = event_dict[key]['sent_info']['sents']
        coref_info = event_dict[key]['sent_info']['coref_info']
        for sent in coref_info:
            for coref in coref_info[sent]['corefs']:
                pronoun = coref[0]
                ref = coref[1]
                if any([word in ref[0] for word in pronoun[0].split()]):
                    pass
                elif any([word in pronoun[0] for word in ref[0].split()]):
                    pass
                elif pronoun[4] - pronoun[3] > 1:
                    pass
                else:
                    try:
                        #Getting the stuff for pronouns
                        if 'coref_tree' in sent_info[pronoun[1]].keys():
                            pronoun_sent = copy.deepcopy(sent_info[pronoun[1]]
                                                         ['coref_tree'])
                        else:
                            pronoun_sent = copy.deepcopy(sent_info[pronoun[1]]
                                                         ['parse_tree'])
                            pronoun_sent = Tree(pronoun_sent)
                        pro_shift = coref_info[pronoun[1]]['shift']
                        #Getting stuff for the reference
                        if 'coref_tree' in sent_info[ref[1]].keys():
                            coref_sent = sent_info[ref[1]]['coref_tree']
                        else:
                            coref_sent = Tree(sent_info[ref[1]]['parse_tree'])
                        ref_shift = coref_info[ref[1]]['shift']

                        #Actaully replacing the pronoun
                        try:
                            pronoun_pos = pronoun_sent.leaf_treeposition(pronoun[3]
                                                                         + pro_shift)
                            #Hunting for the right pronoun
                            if pronoun_sent[pronoun_pos] != pronoun[0]:
                                if pronoun_sent[pronoun_sent.leaf_treeposition(pronoun[3] + (pro_shift - 1))] == pronoun[0]:
                                    pronoun_pos = pronoun_sent.leaf_treeposition(pronoun[3] + (pro_shift - 1))
                                    coref_info[pronoun[1]]['shift'] -= 1
                                elif pronoun_sent[pronoun_sent.leaf_treeposition(pronoun[3] + (pro_shift + 1))] == pronoun[0]:
                                    pronoun_pos = pronoun_sent.leaf_treeposition(pronoun[3] + (pro_shift + 1))
                                    coref_info[pronoun[1]]['shift'] += 1
                                else:
                                    break

                            #Hunting for the right coref
                            original_coref_index = coref_sent.leaf_treeposition(ref[3])[:-2]
                            if ' '.join(coref_sent[original_coref_index].leaves()) == ref[0]:
                                coref_pos = coref_sent.leaf_treeposition(ref[3])[:-2]
                            elif ref[0] in ' '.join(coref_sent[original_coref_index].leaves()):
                                coref_pos = coref_sent.leaf_treeposition(ref[3])[:-2]
                            else:
                                coref_pos = coref_sent.leaf_treeposition(ref[3] + ref_shift)[:-2]

                            if ref[0] not in ' '.join(coref_sent[coref_pos].leaves()):
                                pass

                            #Found everything, now replace
                            coref_tree = Tree('COREF', [coref_sent[coref_pos]])
                            pronoun_sent[pronoun_pos[:-1]] = coref_tree
                        except IndexError:
                            #TODO: Should this use the original sentence rather
                            #than possibly bad coreferences?
                            print """Key {}, sentence {} has a problem with the corefencing. Breaking and moving on.\n""".format(key, sent)
                            break

                        #Recording the shift length for the pronoun replacement
                        if len(coref_tree.leaves()) <= 2:
                            coref_info[pronoun[1]]['shift'] += 0
                        else:
                            coref_info[pronoun[1]]['shift'] += coref_tree.height()

                        coref_info[pronoun[1]]['errors'].append(False)

                        if not any(coref_info[pronoun[1]]['errors']):
                            if pronoun_sent != sent_info[sent]['parse_tree']:
                                sent_info[sent]['coref_tree'] = pronoun_sent
                    except RuntimeError, e:
                        print 'There was an error. {}'.format(e)
                        coref_info[pronoun[1]]['errors'].append(True)
                        pass
    else:
        pass


def _get_np(parse_tree):
    """
    Private function to pull noun phrases from a parse tree.

    Parameters
    ----------

    parse_tree : NLTK.tree object
                Parse tree from which to pull noun phrases.

    Returns
    -------

    output : Dictionary
            Dictionary with two keys: `noun_phrases` and `np_words`.
            `noun_phrases` is a list of noun phrases in the parse tree, while
            `np_words` is a list of words contained in the noun phrases.
    """
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree.subtrees(filter=lambda x: x.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['noun_phrases'] = phrases
    output['np_words'] = words

    return output


def _get_vp(parse_tree):
    """
    Private function to pull verb phrases from a parse tree.

    Parameters
    ----------

    parse_tree : NLTK.tree object
                Parse tree from which to pull verb phrases.

    Returns
    -------

    output : Dictionary
            Dictionary with two keys: `verb_phrases` and `vp_words`.
            `verb_phrases` is a list of verb phrases in the parse tree, while
            `vp_words` is a list of words contained in the verb phrases.
    """
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree.subtrees(filter=lambda x: x.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['verb_phrases'] = phrases
    output['vp_words'] = words

    return output
