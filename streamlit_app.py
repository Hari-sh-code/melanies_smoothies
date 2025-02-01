import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your Smoothie!")

try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error("Could not connect to Snowflake. Please check your connection.")
    session = None 


if session:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_options = my_dataframe["FRUIT_NAME"].tolist()
else:
    fruit_options = []

if "name_on_order" not in st.session_state:
    st.session_state.name_on_order = ""

name_on_order = st.text_input("Name on Smoothie:", placeholder="Enter the name on your smoothie")
name_button = st.button("Submit name")

if name_button and name_on_order:
    st.session_state.name_on_order = name_on_order
    st.write("The name on your smoothie will be:", st.session_state.name_on_order)


if "selected_ingrediants" not in st.session_state:
    st.session_state.selected_ingrediants = []


def update_selection():
    if len(st.session_state.selected_ingrediants) > 5:
        st.warning("You can select up to 5 ingredients", icon="⚠️")
        st.session_state.selected_ingrediants = st.session_state.selected_ingrediants[:5]


st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    key="selected_ingrediants",
    on_change=update_selection
)


time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not st.session_state.name_on_order:
        st.error("Please enter a name for your smoothie before submitting!")
    elif not st.session_state.selected_ingrediants:
        st.error("Please select at least one ingredient for your smoothie!")
    else:
        ingrediants_string = ", ".join(st.session_state.selected_ingrediants)
        
        
        my_insert_stmt = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """
        
        try:
            if session:
                session.sql(my_insert_stmt, params=[ingrediants_string, st.session_state.name_on_order]).collect()
                st.success(f"Your Smoothie is ordered: {st.session_state.name_on_order}", icon="✅")
            else:
                st.error("Snowflake session is not available. Please check your connection.")
        except Exception as e:
            st.error(f"Error submitting order: {e}")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)