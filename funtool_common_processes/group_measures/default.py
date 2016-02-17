# These are the default group measure functions

import funtool.group_measure

def count(group_measure, analysis_collection, state_collection, overriding_parameters=None):
    measure_parameters = funtool.group_measure.get_measure_parameters(group_measure, overriding_parameters)
    analysis_collection.group.measures['count']=len(analysis_collection.group.states)
    return analysis_collection

def average(group_measure, analysis_collection, state_collection, overriding_parameters=None):
    measure_parameters = funtool.group_measure.get_measure_parameters(group_measure, overriding_parameters)
    total=0
    count=0
    for state in analysis_collection.group.states:
        state_value= getattr(state,measure_parameters['average_type']).get(measure_parameters['average_value'])
        if state_value != None:
            total += state_value
            count += 1
    if count != 0:
        analysis_collection.group.measures[group_measure.name]= total/count
    else:
        analysis_collection.group.measures[group_measure.name]= None
    return analysis_collection

def maximum_value(group_measure, analysis_collection, state_collection, overriding_parameters=None):
    measure_parameters = funtool.group_measure.get_measure_parameters(group_measure, overriding_parameters)
    try:
        max_value= max( getattr(state,measure_parameters['value_type']).get(measure_parameters['value'])
                for state in analysis_collection.group.states )
    except:
        max_value= None
    
    analysis_collection.group.measures[group_measure.name]= max_value
    
    return analysis_collection

def minimum_value(group_measure, analysis_collection, state_collection, overriding_parameters=None):
    measure_parameters = funtool.group_measure.get_measure_parameters(group_measure, overriding_parameters)
   
    try:
        min_value= min( getattr(state,measure_parameters['value_type']).get(measure_parameters['value'])
                for state in analysis_collection.group.states )
    except:
        min_value= None

    analysis_collection.group.measures[group_measure.name]= min_value
    
    return analysis_collection
