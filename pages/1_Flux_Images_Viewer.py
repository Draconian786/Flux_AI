import streamlit as st
import fal_client
import pandas as pd
# from dotenv import load_dotenv
import os
from supabase import create_client, Client
import toml

def main():
    # load_dotenv('flux_images.env')
    st.set_page_config(layout="wide")

    SUPABASE_URL = st.secrets['SUPABASE_URL']
    SUPABASE_KEY = st.secrets['SUPABASE_KEY']
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Streamlit app setup
    st.title("Flux AI Images Viewer")

    response = supabase.table("Flux_Image_Repository").select("*").eq('Flux_Image_Convocation_Flag', 'Y').order("Flux_Image_ID", desc=True).execute()
    data = response.data

    # Create two tabs
    tab1, tab2 = st.tabs(["Vertical View", "Card View"])

    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:

            # Loop through the data and print each individual value
            for record in data:
                # st.write("Flux_Image_ID:", record["Flux_Image_ID"])
                st.write("#### **Flux_Image_User_Input:**", record["Flux_Image_User_Input"])
                st.write("##### **Flux_Image_Style:**", record["Flux_Image_Style"])
                # st.write("Flux_Image_Prompt:", record["Flux_Image_Prompt"])
                st.write("##### **Flux_Image_Url:**", record["Flux_Image_Url"])
                st.image(record["Flux_Image_Url"], caption=f'{record["Flux_Image_Style"]} style: {record["Flux_Image_Url"]}', use_column_width=True)
                # st.write("Flux_Image_Created_At:", record["Flux_Image_Created_At"])
                st.write("---")  # Separator for readability

    with tab2:
        # Group records by Flux_Image_User_Input
        grouped_data = {}
        for record in data:
            user_input = record["Flux_Image_User_Input"]
            if user_input not in grouped_data:
                grouped_data[user_input] = []
            grouped_data[user_input].append(record)

        # Loop through each group and display the content
        for user_input, records in grouped_data.items():
            st.write("##### **Flux_Image_User_Input:**", user_input)

            # Display images in groups of 4
            for i in range(0, len(records), 4):
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    if i + j < len(records):
                        with col:
                            st.image(records[i + j]["Flux_Image_Url"], caption=f'{records[i + j]["Flux_Image_Style"]} style', use_column_width=True)

            st.write("---")  # Separator for readability

if __name__ == "__main__":
    main()
