# An adaptor to create and update state_collections based on delimited files

import funtool.adaptor
import funtool.group
import funtool.state_collection
import funtool_common_processes.adaptors.tabular

import csv
import os

# Creates new states from each row in the delimited file. Can create duplicates.
def extend_from_delimited_table(adaptor,state_collection, overriding_parameters=None,loggers=None):
    new_state_collection= create_from_delimited_table(adaptor,state_collection, overriding_parameters,loggers)
    return funtool.state_collection.join_state_collections(state_collection, new_state_collection )

def create_from_delimited_table(adaptor,state_collection, overriding_parameters=None,loggers=None):
    adaptor_parameters= funtool.adaptor.get_adaptor_parameters(adaptor, overriding_parameters)
    if os.path.isfile(adaptor_parameters['file_location']):
        with open(adaptor_parameters['file_location']) as f:
            reader = csv.reader(f, **(_delimiter_parameters(adaptor_parameters, f)))
            state_collection= funtool_common_processes.adaptors.tabular.create_from_config(reader, adaptor_parameters.get('tabular_parameters',{}))
        group= funtool.group.create_group(
                    'file', 
                    state_collection.states, 
                    {}, 
                    {'file':adaptor_parameters['file_location']}, 
                    {})
        state_collection= funtool.state_collection.add_group_to_grouping(state_collection,'file',group, str(adaptor_parameters['file_location']))
    return state_collection
 

def _delimiter_parameters( adaptor_parameters, file_handler):
    params= {}
    if not (adaptor_parameters.get('newline') is None):
        params['newline']= adaptor_parameters['newline']
    if not (adaptor_parameters.get('decoding') is None):
        params['decoding']= adaptor_parameters['decoding']
    if not (adaptor_parameters.get('delimiter') is None):
        params['delimiter']= adaptor_parameters['delimiter']
    if not (adaptor_parameters.get('quoting') is None):
        params['quoting']= adaptor_parameters['quoting']
    if not (adaptor_parameters.get('dialect') is None):
        params['dialect']= adaptor_parameters['dialect']
    else:
        sample_text = ''.join(file_handler.readline() for x in range(3))
        params['dialect'] = csv.Sniffer().sniff(sample_text)
        file_handler.seek(0)
    return params

