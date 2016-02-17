# These are a default set of analysis_selector functions
# A state selector function should accept three parameters a AnalysisSelector, an AnalysisCollection and a StateCollection
#  it should return an AnalysisCollection
# All functions that don't accept (AnalysisSelector,AnalysisCollection,StateCollection) and return AnalysisCollection should
#  be internal functions

import funtool.analysis
import funtool.analysis_selector
import random

def trivial(analysis_selector, analysis_collection, state_collection):
    return analysis_collection

def random_state(analysis_selector, analysis_collection, state_collection):
    return funtool.analysis.AnalysisCollection(random.choice(state_collection.states),None,[])

def previous(analysis_selector, analysis_collection, state_collection):
    """
    Returns an analysis collection with the previous state appended to the state_list
    The previous states can be in a particular grouping or the entire collection

    Can be sorted by state values given as a list with pairs(one item dict) of meta/measure/data and state value names

    Uses the first group in a grouping if there are many
    """
    if 'grouping' in analysis_selector.parameters.keys():
        grouping= analysis_collection.state.groupings.get(analysis_selector.parameters.get('grouping'),[])
        if grouping:
            states= grouping[0].states
        else:
            states= []
    else:
        states= state_collection.states
    if 'sort_by' in analysis_selector.parameters.keys():
        states= _sort_states_list(states, analysis_selector.parameters['sort_by'] ) 
    else:
        states= list(states)
    
    if analysis_collection.state in states:
        state_index= states.index(analysis_collection.state)
        if state_index > 0:
            previous_state= states[state_index-1]
        else:
            previous_state= None
    else:
        previous_state= None    
    new_states_dict= analysis_collection.states_dict.copy()
    new_states_dict['previous']= previous_state
    return funtool.analysis.AnalysisCollection(
        analysis_collection.state,
        analysis_collection.group,
        new_states_dict,
        analysis_collection.groupings)

def _sort_states_list(states, sorting_list):
    converted_sorting_list= _convert_sorting_list(sorting_list)
    return sorted(states, key= lambda state: _get_state_values(state, converted_sorting_list))

def _get_state_values(state, value_list): #value_list is a list of  (attribute, name) tuples
    return [ getattr(state, value_pair[0], {}).get(value_pair[1])
            for value_pair in value_list ]

def _convert_sorting_list(sorting_list): #returns a list of tuples based on dicts
    converted_list= []
    for item_dict in sorting_list:
        for item, item_values in item_dict.items():
            if type( item_values)  == list:
                for item,value in item_values:
                    converted_list.append((item, item_value))
            else:
                converted_list.append((item,item_values))
    return converted_list
            
