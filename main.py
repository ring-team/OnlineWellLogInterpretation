import streamlit as st #1.28.0
from streamlit_drawable_canvas import st_canvas #0.9.3
from PIL import Image
import pandas as pd
import json 
import lasio 
import lasio.examples
import matplotlib.pyplot as plt
import numpy as np



def main():


    # Organisation de l'app :
    #   - Présentation de l'expérience
    #   - Introduction du questionnaire et questionnaire -> Quelles catégories ?
    #   - Introduction à l'exercice d'interpretation
    #   - Affichage des données à interpreter
    #   - Entrée de l'interprétation -> Quel format ?
    #   - Récupération de l'interpretation ? -> Comment ?


    st.set_page_config(layout="wide")  # Utilise toute la largeur de l'écran


    #Presentation de l'experience

    st.title("Welcome to the well log interpretation uncertainties experiment !")

    st.write("The goal of this experiment is to 'quantify' the impact of an individual background and prior experiences in its interpretation of well log data.")
    st.write("For that it is needed to obtain interpretation from various individuals of varying background, experiences and field.")
    st.write("To participate you only need to complete the little form about 'who' you are and then to interprete the data presented to you and send the answer !")
    st.write("Also, any feedback on the experiment is welcomed ! Be it on the clarity of the instructions, the GUI etc...")

    #Introduction du questionnaire
    st.title("Here is the form.")

    #Questionnaire
    status = st.text_input("Are you a student, a professional engineer or a researcher ?", "**Your status**")
    field = st.radio(
        "What is your geosciences field ?",
        ["Stratigraphy", "Geology", "Geophysics", "Petrophysics", "Sedimentology", "Formation evaluation", "Geomodeling", "Statistics or geostatistics", "Machine Learning", "Applied Mathematics", "None of the above"]
    )

    other_field = st.text_input("If you selected 'None of the above', please specify your field :", "**Your field**")

    years = st.number_input(
        "How many years of professional experience do you have in geosciences ?", value=None, placeholder="Type a number..."
    )

    confidence = st.radio(
        "How confident are you on well log interpretation ?",
        ["I am the best there is", "I'm excellent", "I'm quite good", "Neutral", "not particularly confident", "Not confident", "First time in my life I see well log data", "Geosciences ? What's that ?"]
    )

    #Enregistrement des réponses dans un fichier JSON

    data = {
        "Status": status,
        "field": field,
        "other_field": other_field,
        "years": years,
        "confidence": confidence

    }

    if st.button("Download your answers in a JSON file !"):
        with open(r"C:\Users\e3812u\Documents\Projet_3A\OnlineWellLogInterpretation\Results\test.json", "w") as f:
            json.dump(data, f)

    #Introduction à l'expérience d'interpretation
    st.title("The interpretation experiment")
    st.write("Now that you have filled the form you can go ahead and interprete the data presented in the next section.")
    st.write("The objective is for you to make annotations, to write ideas and basically any form of interpretation of the data you can think of.")

    #Présentation des données a interpreter
    st.title("Data presentation")
    st.write("The data you are to interprete is/is from a public dataset available on INSERT DATA ORIGIN")



    #Interpretation
    st.title("Interpretation")


    #Chargement des donnees
    # Load the LAS file
    las = lasio.examples.open("1001178549.las")
    df = las.df()

    st.title("Well Log Visualization - Grouped by Type")
    st.dataframe(df)

    # Configuration
    logs_per_row = st.slider("Logs per row", min_value=3, max_value=8, value=5)
    fig_height = st.slider("Figure height", min_value=6, max_value=15, value=10)

    # Define log groups (common well log types)
    log_groups = {
        'Gamma Ray': ['GR', 'CGR', 'SGR', 'HSGR', 'THOR', 'URAN', 'POTA'],
        'Resistivity': ['ILD', 'ILM', 'ILS', 'SFLU', 'LLD', 'LLS', 'MSFL', 'RES', 'RT', 'RILD', 'RILM'],
        'Porosity': ['NPHI', 'DPHI', 'RHOB', 'DT', 'PHIT', 'PHIE', 'DTS', 'DTSM'],
        'Sonic': ['DT', 'DTC', 'DTS', 'DTCO', 'DTSM', 'AC', 'SONIC'],
        'Density': ['RHOB', 'RHOZ', 'ZDEN', 'DRHO', 'DEN'],
        'Neutron': ['NPHI', 'TNPH', 'NPOR', 'NEU'],
        'Caliper': ['CALI', 'CAL', 'HCAL', 'C1', 'C2'],
        'SP': ['SP', 'SPT'],
        'Other': []
    }

    # First, display what columns we have
    st.write(f"**Total logs available: {len(df.columns)}**")
    st.write("Columns:", df.columns.tolist())

    # Categorize columns into groups
    categorized = {group: [] for group in log_groups.keys()}
    used_columns = set()

    for column in df.columns:
        column_upper = column.upper()
        assigned = False
        
        for group_name, keywords in log_groups.items():
            if group_name == 'Other':
                continue
            for keyword in keywords:
                if keyword in column_upper:
                    categorized[group_name].append(column)
                    used_columns.add(column)
                    assigned = True
                    break
            if assigned:
                break
        
        if not assigned:
            categorized['Other'].append(column)

    # Display each group
    for group_name, group_columns in categorized.items():
        if not group_columns:
            continue
        
        st.write(f"## {group_name} Logs ({len(group_columns)} logs)")
        st.write(f"Logs: {', '.join(group_columns)}")
        
        # Calculate rows needed for this group
        n_logs = len(group_columns)
        n_rows = int(np.ceil(n_logs / logs_per_row))
        
        # Create plots for each row in this group
        for row in range(n_rows):
            start_idx = row * logs_per_row
            end_idx = min(start_idx + logs_per_row, n_logs)
            row_columns = group_columns[start_idx:end_idx]
            
            # Create figure for this row
            fig, axes = plt.subplots(1, len(row_columns), figsize=(15, fig_height), sharey=True)
            
            # Handle case where there's only one subplot
            if len(row_columns) == 1:
                axes = [axes]
            
            for i, column in enumerate(row_columns):
                axes[i].plot(df[column], df.index, linewidth=0.8)
                axes[i].set_xlabel(column, fontsize=10, fontweight='bold')
                axes[i].invert_yaxis()  # Depth increases downward
                axes[i].grid(True, alpha=0.3)
                axes[i].tick_params(labelsize=8)
            
            axes[0].set_ylabel('Depth', fontsize=10, fontweight='bold')
            plt.suptitle(f'{group_name} - Row {row + 1}', fontsize=12, fontweight='bold')
            plt.tight_layout()
            
            st.pyplot(fig)
            plt.close(fig)
        
        st.divider()

    st.success("✓ All logs displayed!")


    # Specify canvas parameters in application
    col1, col2, col3 = st.columns([1, 1, 1])
    drawing_mode = col1.selectbox(
        "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform")
    )

    stroke_width = col2.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == 'point':
        point_display_radius = col2.slider("Point display radius: ", 1, 25, 3)
    stroke_color = col1.color_picker("Stroke color hex: ")
    #bg_color = col3.color_picker("Background color hex: ", "#eee")
    bg_image =  r"Data\test_well_log.png" #Forced background = well log.

    realtime_update = col3.checkbox("Update in realtime", True)

        

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        #background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=realtime_update,
        height=750,
        width=800,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        key="canvas",
    )

    



if __name__ == "__main__":
    main()
