import streamlit as st
import fal_client
import pandas as pd
# from dotenv import load_dotenv
import os
from supabase import create_client, Client
import toml

def main():
    # load_dotenv('flux_images.env')

    SUPABASE_URL = st.secrets['SUPABASE_URL']
    SUPABASE_KEY = st.secrets['SUPABASE_KEY']
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Streamlit app setup
    st.title("Flux AI Image Generator")
    tab1, tab2 = st.tabs(["Single Generation", "Batch Generation"])

    with tab1:
        st.write("Enter a prompt to generate an image:")

        # User input
        user_prompt = st.text_input("Prompt",
                                    "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word FLUX is painted over it in big, white brush strokes with visible texture.")
        # Dropdown for selecting image size
        image_size = st.selectbox(
            "Select Image Size",
            ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"]
        )

        if st.button("Generate Image"):
            with st.spinner("Generating image..."):
                # Submit the prompt to the fal_client
                handler = fal_client.submit(
                    "fal-ai/flux-pro",
                    # "fal-ai/flux/dev",
                    arguments={
                        "prompt": user_prompt,
                        "image_size": image_size,
                        "enable_safety_checker": False,
                    },
                )

                # Get the result
                result = handler.get()

                # st.write(result)

                # Extract the image URL from the result
                image_url = result["images"][0]["url"]

                # Display the result
                st.image(image_url, caption=image_url, use_column_width=True)

    with tab2:
        st.write("Upload a CSV file containing prompts:")

        # Style descriptions
        styles = {
            "Cinematic": "hyper realistic, lens flare, atmosphere, glowing, detailed, intricate, full of color, cinematic lighting, art station trends, 4k, hyperrealism, out of focus, extreme detail, unreal engine 5, film, masterpiece",
            "Pop Art": "in the style of aggressive digital illustration, bold shadows, airbrush art, close-up, pop art color palette, ultra hd, comic art",
            "Comic": "in the style of Moebius, Josan Gonzalez, Peter Max, Roy Lichtenstein, Jodorowsky, Atey Ghailna, Lisa Frank, a full shot in the comic book style with flat colors, ink outlines, bold lines, high contrast, and a vibrant color palette",
            "Oil Painting": "impasto, sfumato, chiaroscuro, palette knife, oil painting, impressionist style, vibrant colors, detailed brushstrokes, textured canvas effect, impressionistic technique, high resolution"
        }

        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        # Dropdown for selecting image size
        image_size_batch = st.selectbox(
            "Select Image Size for Batch Generation",
            ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"]
        )

        if uploaded_file is not None:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)

            # Check if the CSV has a column named 'prompt'
            if 'Prompt' in df.columns:
                if st.button("Generate Images"):
                    for index, row in df.iterrows():
                        user_prompt = row['Prompt']

                        # Concatenate styles to the prompt
                        for style_name, style_description in styles.items():
                            styled_prompt = f"{user_prompt}, {style_description}"

                            st.write(f"##### **{style_name} style**: \n\n {user_prompt}")

                            with st.spinner("Generating image..."):
                                # Submit the prompt to the fal_client
                                handler = fal_client.submit(
                                    "fal-ai/flux-pro",
                                    arguments={
                                        "prompt": styled_prompt,
                                        "image_size": image_size_batch,
                                        "enable_safety_checker": False,
                                    },
                                )

                                # Get the result
                                result = handler.get()

                                # Extract the image URL from the result
                                image_url = result["images"][0]["url"]

                                # Display the result
                                st.image(image_url, caption=f"{style_name} style: {image_url}", use_column_width=True)

                                # st.write(result)

                                flux_image_repository_data_to_insert = {
                                    "Flux_Image_Style": style_name,
                                    "Flux_Image_User_Input": user_prompt,
                                    "Flux_Image_Prompt": styled_prompt,
                                    "Flux_Image_Url": image_url,
                                    "Flux_Image_Convocation_Flag": "Y",
                                }

                                fl_response = supabase.table("Flux_Image_Repository").insert(flux_image_repository_data_to_insert).execute()

            else:
                st.error("CSV file must contain a 'prompt' column.")

if __name__ == "__main__":
    main()
