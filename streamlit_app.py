import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(""" Choose the Fruits you want in your Smoothie.""")

name_of_order = st.text_input('Name on smoothie:')
st.write('The name on your smoothie will be:', name_of_order)

# Connect to Snowflake and retrieve data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('search_on'))

# Debugging: Print Snowpark DataFrame
st.write("Snowpark DataFrame Preview:")
st.write(my_dataframe.show())  # Show rows for debugging

# Convert to Pandas
try:
    pd_df = my_dataframe.to_pandas()
    st.write("Pandas DataFrame Preview:")
    st.write(pd_df)  # Show Pandas DataFrame in Streamlit
except Exception as e:
    st.write(f"Error: {e}")

# Use Pandas DataFrame for the multiselect options
ingredients_lists = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use Pandas list of fruit names for the options
    max_selections=5
)

if ingredients_lists:
    ingredients_string = ''
    for fruit_chosen in ingredients_lists:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(f"{fruit_chosen} nutrition information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_of_order}')
    """
    time_to_insert = st.button('Submit order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
