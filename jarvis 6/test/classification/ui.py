import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

# Set up the Streamlit app
st.title("Text Classification Dashboard")

# Upload CSV File
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])


def get_predicted_label(new_example, label_prototypes):
    new_embedding = model.encode([new_example])
    similarities = {
        label: cosine_similarity(new_embedding, prototype.reshape(1, -1))[0][0]
        for label, prototype in label_prototypes.items()
    }
    return max(similarities, key=similarities.get)

def display_result(predicted_label):
    color_map = {
        'Label1': '#FF5733',  # Red
        'Label2': '#33FF57',  # Green
        'Label3': '#3357FF',  # Blue
        'Label4': '#F3FF33',  # Yellow
        'Label5': '#FF33A6',  # Pink
    }

    result_color = color_map.get(predicted_label, '#FFFFFF')  # Default to white if label not found
    st.markdown(f"<div style='background-color: {result_color}; padding: 10px; border-radius: 5px;'>"
                 f"<h3 style='color: white;'>Predicted Label: {predicted_label}</h3></div>",
                 unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        # Load the data
        data = pd.read_csv(uploaded_file)

        # Check for required columns
        if 'Examples' not in data.columns or 'Labels' not in data.columns:
            st.error("CSV file must contain 'Examples' and 'Labels' columns.")
        else:
            st.success("File loaded successfully!")

            # Display basic data information
            st.subheader("Data Overview")
            st.write("Shape of the dataset:", data.shape)
            st.write("Columns in the dataset:", data.columns.tolist())
            st.write("First few rows of the dataset:")
            st.dataframe(data.head())

            # Display unique labels and their counts
            label_counts = data['Labels'].value_counts()
            st.subheader("Unique Labels")
            st.write("Total unique labels:", label_counts.count())
            st.write(label_counts)

            # Create prototypes for each label
            embeddings = model.encode(data['Examples'].tolist())
            label_prototypes = {}
            for label in set(data['Labels']):
                label_embeddings = embeddings[data['Labels'] == label]
                label_prototypes[label] = np.mean(label_embeddings, axis=0)

            # Input for new example
            new_example = st.text_input("Enter a text to classify:")
            
            if st.button("Classify Text"):
                if not new_example.strip():
                    st.warning("Please enter a sentence to classify.")
                else:
                    predicted_label = get_predicted_label(new_example, label_prototypes)
                    st.markdown(f"### Predicted Label: **{predicted_label}**", unsafe_allow_html=True)
                    # display_result(predicted_label)

    except Exception as e:
        st.error(f"Failed to load file: {e}")



