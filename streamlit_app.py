# Import python packages
import streamlit as st
import requests
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """ Choose the Fruits you want in your Smoothie.
    """
)
 
 
name_of_order = st.text_input ('name on smoothie:')
st.write ('the name on your smoothie will be:')
 
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()
 
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()
                            
 
ingredients_lists =  st.multiselect(
    'choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
 
if ingredients_lists:
    # st.write (ingredients_lists)
    # st.text (ingredients_lists)
 
    ingredients_string =''
    for fruit_chosen in ingredients_lists:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader (fruit_chosen + 'nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on) 
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    # st.write (ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_of_order+ """')"""
    time_to_insert = st.button('submit order')
    # st.write(my_insert_stmt)
    # st.stop()
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
