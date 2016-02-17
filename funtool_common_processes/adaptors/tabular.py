# This is a simple adaptor to generate a state_collection from a tabular object. Mostly meant to be used as a library for adaptors which import a raw table.

import funtool.adaptor

import funtool.state_collection
import funtool.state
import funtool.group
import funtool.grouping_selector


def clear_state_collection(adaptor,state_collection, overriding_parameters=None,loggers=None):
    """
    Returns a new empty state collection
    """
    state_collection = funtool.state_collection.StateCollection([],{})
    return state_collection


def create_from_config( row_reader, config ):
    """
    Returns a state_collection by using create_tabular_state_collection after generating state and groupings columns from the config

    """
    state_columns= format_columns_dict(config.get('state',{}) )
    groupings_params= reformat_groupings_columns( config.get('groupings',{}), format_columns_dict )

    # Substitue row index for column names
    if not config.get('use_column_number',False):
        if config.get('column_headers',False):
            header_row= config.get('column_headers')
        else:
            header_row= next(row_reader)
        state_columns= substitute_column_indices(state_columns, header_row)
        groupings_params= reformat_groupings_columns( groupings_params, substitute_column_indices, [header_row] )
    else:
        first_row= next(row_reader)
        header_row= list(range(len(first_row)))
        row_reader= prepend_rows([first_row], row_reader)
        if config.get('column_headers',False): #Use number and headers
            header_row= [ config.get('column_headers')[i] if len(config.get('column_headers')) > i else i for i in header_row ] 
            state_columns= substitute_column_indices(state_columns, header_row)
            groupings_params= reformat_groupings_columns( groupings_params, substitute_column_indices, [header_row] )

    # Include all other columns as specified type #TODO extend to groupings
    if not (config.get('include_all_others_as') is None):
        state_attrib= config.get('include_all_others_as')
        if state_attrib in ['meta','measure','data']: #funtool.state.State._fields excluding id and groupings
            all_assigned_columns= []
            for attrib in ['meta','measure','data']:
                all_assigned_columns.append(state_columns.get(attrib))
            for grouping_name, grouping_values in groupings_params.items():
                for grouping_value_name, values in grouping_values.items():
                    if grouping_value_name is 'columns':
                        for attrib in ['meta','measure','data']: 
                            all_assigned_columns.append(values.get(attrib))
            all_assigned_columns= [ columns for columns in all_assigned_columns if not (columns is None) ]
            try:
                state_columns[state_attrib].update(unspecified_columns(header_row, all_assigned_columns))
            except KeyError:
                state_columns[state_attrib]= unspecified_columns(header_row, all_assigned_columns)
    
    if config.get('default_values') is None:
        default_values={}
    else:
        default_values= config.get('default_values')


    return create_tabular_state_collection( row_reader, state_columns, create_groupings_columns(groupings_params), default_values )

def create_tabular_state_collection(row_reader, state_columns, groupings_columns, default_value={}):
    """
    Returns a state_collection created by iterating through row_reader, which should return a list for each row

    state_columns is a dict with values for data, measures, and meta
        each value should consist of a dict with sub-values name:row_index

        For example:
            { 'data': { 'user_action':5 },
              'meta': { 'project_id':0, 'user_id':1 },
              'measures': { 'user_score':3 }
            }

    groupings_columns is a dict of grouping_name:grouping_columns
        where grouping_columns is like state_columns, but with an additional id_index 
        id_index is the row index of the values used to create a group
        use id_indicies to group on multiple columns

                
    """
    state_collection= funtool.state_collection.StateCollection(states=[],groupings={})
    for row in row_reader:
        state= funtool.state.State(
            id=None,
            data=dict(row_dict(row, state_columns.get('data',{}) ), **(default_value.get('data',{}))),
            measures=dict(row_dict(row, state_columns.get('measures',{}) ), **(default_value.get('measures',{}))),
            meta=dict( row_dict(row, state_columns.get('meta',{}) ), **(default_value.get('meta',{}))),
            groupings={})
        state_collection.states.append(state)
        for grouping_name, grouping_columns in groupings_columns.items():
            grouping_id= create_grouping_id(grouping_columns, row )
            if state_collection.groupings.get(grouping_name) is None:
                state_collection.groupings[grouping_name]= {}
            if state_collection.groupings[grouping_name].get(grouping_id) is not None:
                funtool.group.add_state_to_group(state_collection.groupings[grouping_name].get(grouping_id), state)
            else:
                group= funtool.group.Group(
                    grouping_name, 
                    [state], 
                    row_dict(row, grouping_columns.get('measures',{})), 
                    row_dict(row, grouping_columns.get('meta',{})), 
                    row_dict(row, grouping_columns.get('data',{})))
                state_collection.groupings[grouping_name][grouping_id]= group 
    return state_collection 

def row_dict(row, columns_dict):
    """
    Returns a dict based on columns_dict

    columns_dict should be a dict with name:row_index values
    """

    return { column_name: row[column_index] for column_name, column_index in columns_dict.items() }

def unspecified_columns(column_names, column_dicts):
    """
    column_names is a list of strings (i.e. the header row)

    column_dicts is a list of column_dict which have name:index values

    Returns a dict with values name:row_index for each column not included in any column dict 

    Useful for cases when all columns to be included are not specified
    """
    dup_column_names= list(column_names)
    for column_dict in column_dicts:
        for i in column_dict.values():
            dup_column_names[i]= None
    
    return { column_name: column_index for column_index, column_name in enumerate(dup_column_names) if column_name is not None }
        
def create_grouping_id(grouping_columns,row):
    if not grouping_columns.get('id_indecies') is None:
        if not grouping_columns.get('id_index') is None:
            print('Warning: Both id_index and id_indecies are set. Defaulting to id_indecies')
        return tuple([ row[i] for i in grouping_columns.get('id_indecies') ])
    elif not grouping_columns.get('id_index') is None:
        return row[grouping_columns.get('id_index')]
    else:
        return None

def substitute_column_indices(state_columns, column_names): # returns a new copy does not edit original state_columns
    new_state_columns={}
    for state_attrib,state_values_dict in state_columns:
        new_state_columns[state_attrib]={}
        for state_value_name,column_name in state_values_dict.items():
            try:
                new_state_columns[state_attrib][state_value_name]= column_names.index(column_name)
            except ValueError:
                print('WARNING: Column {} is missing. Proceeding with that column.'.format(column_name))

    return new_state_columns

def format_columns_dict(yaml_config, attrib_names=['meta','measures','data']):
    """
    Coverts a dict from config format to columns format used by tabular functions

    attrib_names is a list of possible attributes. If None, all are possible.

    In YAML:
        
        column name: state/group attribute

        or

        column name: state/group attribute: state/group attribute value name

        for example:

        user_id: meta

        or 

        "User Action": data: user_action

    To:

        state/group attribute: state/group attrbute value name: column_name




    """
    tabular_columns={}
    for column_name,attrib_item in yaml_config.items():
        if isinstance(attrib_item, str):
            tabular_columns= set_reformatted_item( tabular_columns, attrib_item, column_name, column_name, attrib_names )
        elif isinstance(attrib_item, dict):
            (attrib_name,value_name)= next(iter(attrib_item.items()))
            tabular_columns= set_reformatted_item( tabular_columns, attrib_name, value_name, column_name, attrib_names )
    return tabular_columns

def set_reformatted_item( reformatted_items, attrib_item, value_name, column_name, attrib_names):
    if (not attrib_names is None) and attrib_item in attrib_names:
        try:
            reformatted_items[attrib_item][value_name]=column_name
        except KeyError:
            reformatted_items[attrib_item]={value_name: column_name}
    return reformatted_items


def prepend_rows(rows, row_reader):
    """
    Creates a new generator with rows prepended.

    Useful to return a record row misread as a header row
    """
    for row in rows:
        yield row
    for row in row_reader:
        yield row
            
def reformat_groupings_columns(groupings, reformat_function, function_params=None):
    """
    Runs the reformat_fuction on the columns of each grouping, adds optional *function_params to function call

    Returns a new groupings dict with reformatted columns
    """
    new_groupings={}
    for grouping_name,grouping_values in groupings.items():
        new_groupings[grouping_name]={}
        for grouping_value_name, values in grouping_values.items():
            if grouping_value_name is 'columns':
                if function_params is None:
                    new_groupings[grouping_name][grouping_value_name]= reformat_function(values)
                else:
                    new_groupings[grouping_name][grouping_value_name]= reformat_function(values, *function_params)
            else:
                new_groupings[grouping_name][grouping_value_name]=values
    return new_groupings

def create_groupings_columns(groupings_params):
    """
    Strips all other parameters from groupings except name and columns
    """
    new_groupings={}
    for grouping_name, grouping_values in groupings_params.items():
        for values_name, values in grouping_values.items():
            if values_name is 'columns':
                new_groupings[grouping_name]=values
    return new_groupings
