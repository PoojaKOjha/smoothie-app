# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders! :cup_with_straw:")
st.write("Orders that need to be filled.")

# Connect to Snowflake
cnx = st.connection("snowf lake")
session = cnx. session()

# Load only unfilled orders
my_dataframe = (
    session.table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)


if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    my_insert_stmt = """ insert into smoothies.public.orders (name_on_order, ingredients)
        values ('""" + name_on_order + """', '""" + ingredients_string + """') """
    st.stop()

time_to_insert = st.button('Submit Order')

# If there are pending orders, show the editor


if my_dataframe:
    editable_df = st.data_editor(my_dataframe)

    submitted = st.button('Submit')

    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)

        try:
            og_dataset.merge(
                edited_dataset,
                (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
                [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
            )
            st.success("Order(s) Updated!", icon="👍")
        except Exception as e:
            st.write("Something went wrong.")
            st.write(e)

else:
    st.success("There are no pending orders right now.", icon="👍")

