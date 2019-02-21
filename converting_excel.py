import pandas as pd
import numpy as np 


def permute(array):
    '''
        Returns the new list by making permutations of array elements
    '''
    if len(array)==1:
        return array
    else:
        temp_list=[]
        for i in array:
            other_elements=list(set(array)-set([i]))
            small_output=permute(other_elements)
            temp_list.extend(small_output)
            for j in small_output:
                temp_list.append(i+" " +j)
        return temp_list


# Reading input file into dataframe


def make_key_value(input_file):
    df_input=pd.read_excel(input_file)
    # Now, deleting all the columns and rows with  only nan values in the input values 
    columns=df_input.columns
    for column in columns:
        if df_input[column].isnull().all():
            df_input.drop(columns=column, inplace=True)

    for index, row in df_input.iterrows():
        if row.isnull().all():
            df_input.drop(index,inplace=True)
    column=df_input.columns[0]
    waste_headings=[]        #it stores those heading where we don't have any values further 
    key_value_dictionary={}   #it stores key value pairs
    total_columns=df_input.shape[1]
    for idx,row in df_input.iterrows():
        if row.isna().sum()==total_columns-1:
            ''' 
                It means nan values are for all the columns except the heading one hence it should go to waste_heading 
                which is of no purpose to us 
            '''
            waste_headings.append(row[0].lower())
        else:
            key_value_dictionary[row[0].lower()]=list(row[1:])
    redundant_keys_in_dict=[]  ##it stores redundant keys such as  Total Rental income
    logic_defy_words=[]  #words where our klogic does not work 
    for heading in waste_headings:
        if 'total ' + heading in key_value_dictionary:
            redundant_keys_in_dict.append('total '+heading)
        else:
            logic_defy_words.append(heading)
            array=heading.strip().split(" ")
            combinations=permute(array)
            for i in combinations:
                if 'total '+i in key_value_dictionary:
                    redundant_keys_in_dict.append('total '+i)
    # Now we have a dictionary, with 'Total Rental Losses' type strings included whiuch should not be there. We can remove it. using redundant_keys found above.
    for i in redundant_keys_in_dict:
        key_value_dictionary.pop(i,None)
    final_df=pd.DataFrame.from_dict(key_value_dictionary).T
    filename_to_save='result_'+input_file.split('/')[-1]
    final_df.to_excel(filename_to_save)

# make_key_value('/home/shivam/Desktop/FlaskMCube/Test 1 - (Excel).xlsx')
