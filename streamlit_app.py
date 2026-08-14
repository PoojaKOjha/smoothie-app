# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# -----------------------------
# PAGE TITLE
# -----------------------------
st.title("Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------
# CONNECT TO SNOWFLAKE
# -----------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------
# LOAD FRUIT OPTIONS
# -----------------------------
fruit_df_sp = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert Snowpark → Pandas
pd_df = fruit_df_sp.to_pandas()

# -----------------------------
# NAME ON SMOOTHIE
# -----------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------
# MULTISELECT
# -----------------------------
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# -----------------------------
# SHOW NUTRITION INFO USING SEARCH_ON
# -----------------------------
ingredients_string = ""

if ingredient_list:
    for fruit_chosen in ingredient_list:

        # Build ingredients string
        ingredients_string += fruit_chosen + " "

        # Get correct search term
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API call using SEARCH_ON
        fruityvice_response = requests.get(
            f"https://fruityvice.com/api/fruit/{search_on}"
        )

        st.dataframe(
            fruityvice_response.json(),
            use_container_width=True
        )

# -----------------------------
# INSERT ORDER INTO SNOWFLAKE
# -----------------------------
if st.button("Submit Order"):

    if not name_on_order:
        st.error("Please enter a name for the smoothie.")
    elif not ingredient_list:
        st.error("Please choose at least one ingredient.")
    else:
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
        """

        try:
            session.sql(insert_stmt).collect()
            st.success("Order submitted!", icon="👍")
        except Exception as e:
            st.error("Something went wrong.")
            st.write(e)
