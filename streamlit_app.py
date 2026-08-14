# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col, when_matched

# -----------------------------
# PAGE TITLE
# -----------------------------
st.title(":cup_with_straw: Pending Smoothie Orders! :cup_with_straw:")
st.write("Orders that need to be filled.")

# -----------------------------
# CONNECT TO SNOWFLAKE
# -----------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------
# PART 1 — FRUIT OPTIONS TABLE
# -----------------------------
fruit_df_sp = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

st.subheader("Fruit Options Table")
st.dataframe(fruit_df_sp, use_container_width=True)

# Convert Snowpark → Pandas
fruit_df = fruit_df_sp.to_pandas()

# -----------------------------
# PART 2 — MULTISELECT USING FRUIT_NAME
# -----------------------------
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# -----------------------------
# PART 3 — LOOP THROUGH SELECTED FRUITS
# -----------------------------
if ingredient_list:
    for fruit_chosen in ingredient_list:

        # Get correct search term
        search_on = fruit_df.loc[
            fruit_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fruityvice API call using SEARCH_ON
        fruityvice_response = requests.get(
            "https://fruityvice.com/api/fruit/" + search_on
        )

        fruityvice_json = fruityvice_response.json()
        st.json(fruityvice_json)

# -----------------------------
# PART 4 — PENDING ORDERS TABLE
# -----------------------------
st.subheader("Pending Orders")

orders_sp = (
    session.table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
)

st.dataframe(orders_sp, use_container_width=True)

# -----------------------------
# PART 5 — EDIT PENDING ORDERS
# -----------------------------
editable_df = st.data_editor(orders_sp)

submitted = st.button("Submit Updates")

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
        st.error("Something went wrong.")
        st.write(e)
