import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

from langchain.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

API_KEY = open('GOOGLE_API_KEY').read()
SEARCH_ENGINE_KEY = open('SEARCH_ENGINE_API').read()

# Google Custom Search API setup for image fetching
GOOGLE_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')


def add_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://images.pexels.com/photos/7722967/pexels-photo-7722967.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1');
            background-size: cover; /* or use 'contain' */
            background-position: center; /* Adjusts the position of the image */
            background-repeat: no-repeat; /* Prevents the image from repeating */
            filter: blur(0px); /* Adjust blur effect */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local('faiss_index')


def get_conversational_chain():
    prompt_template = """
    Act Like a Chemistry teacher. Answer the questions in terms of chemistry.
    Answer the question as detailed as possible from the provided context. If the answer is not available 
    in the context, search from the web.
    Show some images you found on the internet.

    Context: {context}
    Question: {question}

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    return chain


def fetch_images(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_KEY}&key={API_KEY}&searchType=image&num=3"
    response = requests.get(search_url)
    image_urls = []

    if response.status_code == 200:
        results = response.json().get("items", [])
        for result in results:
            image_urls.append(result["link"])
    else:
        st.write("Error fetching images.")

    return image_urls


# List of 50 chemistry-related keywords
chemistry_keywords = [
    # Basic Chemistry
    'atom', 'molecule', 'element', 'compound', 'mixture', 'reaction', 'bond', 'acid', 'base', 'pH', 
    'ion', 'electron', 'proton', 'neutron', 'valence', 'covalent bond', 'ionic bond', 'metal', 
    'non-metal', 'salt', 'solution', 'solvent', 'solute', 'suspension', 'colloid', 'chemical formula',
    'mass', 'volume', 'density', 'molar mass', 'stoichiometry', 'reactant', 'product', 'yield', 'chemistry',

    # Intermediate Chemistry
    'oxidation', 'reduction', 'redox', 'functional group', 'hydrocarbon', 'alkane', 'alkene', 
    'alkyne', 'isomer', 'ester', 'ketone', 'aldehyde', 'carboxylic acid', 'amine', 'ether', 
    'phenol', 'nitrile', 'thermochemistry', 'endothermic', 'exothermic', 'neutralization', 
    'reaction mechanism', 'catalyst', 'enzyme', 'buffer', 'molarity', 'molality', 'titration', 
    'concentration', 'dilution', 'crystal lattice', 'alloy', 'phase change', 'gas laws', 
    'ideal gas', 'real gas', 'partial pressure', 'dilute solution', 'concentrated solution', 

    # Advanced Chemistry
    'quantum chemistry', 'thermodynamic', 'Gibbs free energy', 'Le Chatelier’s principle', 
    'kinetic molecular theory', 'reaction kinetics', 'activation energy', 'transition state', 
    'catalytic cycle', 'spectroscopy', 'chromatography', 'analytical chemistry', 'mass spectrometry', 
    'NMR spectroscopy', 'X-ray diffraction', 'valence shell', 'molecular orbital theory', 
    'crystal structures', 'coordination compounds', 'ligand', 'oxidation state', 'redox titration', 
    'thermodynamic equilibrium', 'chemical equilibrium', 'dynamic equilibrium', 'colligative properties', 
    'colloids', 'heterogeneous catalysis', 'homogeneous catalysis', 'bioinorganic chemistry', 

    # Specialized Topics
    'organic synthesis', 'metallurgy', 'nanotechnology', 'green chemistry', 'photochemistry', 
    'photophysics', 'polymer chemistry', 'biochemistry', 'neurochemistry', 'astrochemistry', 
    'environmental chemistry', 'materials science', 'surface chemistry', 'medicinal chemistry', 
    'supramolecular chemistry', 'chemical ecology', 'forensic chemistry', 

    # Emerging Fields
    'cheminformatics', 'computational chemistry', 'data science in chemistry', 'machine learning in chemistry',
    'neuro-symbolic AI in chemistry', 'quantum computing in chemistry', 'catalysis', 'photocatalysis',
    'artificial photosynthesis', 'carbon capture', 'green synthesis', 'sustainable chemistry'
]


# Function to check if the query is chemistry-related
def is_chemistry_related(query):
    return any(keyword.lower() in query.lower() for keyword in chemistry_keywords)


def user_input(user_question):
    # Check if the question is related to chemistry
    if not is_chemistry_related(user_question):
        st.write("Sorry, I can only respond to chemistry-related questions.")
        return

    # Process the chemistry-related question
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
    new_db = FAISS.load_local('faiss_index', embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )

    answer = response['output_text']
    st.write('Reply: ', answer)

    # Store the question and answer in session state
    st.session_state.qa_history.append((user_question, answer))

    # Fetch and display images related to the user question
    st.write("Here are some images related to your search:")
    image_urls = fetch_images(user_question)
    if image_urls:
        for url in image_urls:
            st.image(url, width=300)


# Set the page configuration at the start of the script
st.set_page_config(page_title="Study Assistant")

# Custom CSS to change font sizes
st.markdown(
    """
    <style>
    .header {
        text-align: center; /* Align text to the center */
        position: absolute; /* Position it at the top */
        top: 10px; /* Adjust distance from the top */
        left: 50%; /* Adjust distance from the left */
        transform: translateX(-50%); /* Center the header */
        width: 100%; /* Full width for alignment */
    }

    .big-font {
        font-size: 30px;
        color: #FFD700;  /* Gold color for emphasis */
        font-family: 'Courier New', monospace; /* Monospaced font for a techy look */
        font-weight: bold; /* Make it bold */
    }

    .medium-font {
        font-size: 20px;
        color: black;  /* Light gray for secondary text */
        font-family: 'Verdana', sans-serif; /* Cleaner font style */
    }

    .stButton > button {
        background-color: #FF5733;  /* Vibrant red-orange */
        border: none;               
        color: white;              
        padding: 14px 30px;       
        text-align: center;         
        text-decoration: none;      
        display: inline-block;      
        font-size: 16px;           
        margin: 4px 2px;          
        cursor: pointer;           
        border-radius: 20px;        
        transition: background-color 0.3s; 
    }

    .stButton > button:hover {
        background-color: #C70039; /* Darker red on hover */
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True  # Allows the HTML to be rendered correctly
)

# Function to convert units
def unit_converter():
    with st.expander("Unit Convertions", expanded=True):

        # Custom styling for the title
        st.markdown('<h2 style="font-size: 28px;">Chemistry Unit Converter</h2>', unsafe_allow_html=True)
        option = st.selectbox("Select Conversion Type", ["Moles to Grams", "Grams to Moles", "Molarity Calculation", "Liters to Moles"])
        if option == "Moles to Grams":
            moles = st.number_input("Enter Moles:")
            molar_mass = st.number_input("Enter Molar Mass (g/mol):")
            if st.button("Convert"):
                grams = moles * molar_mass
                st.write(f"{moles} moles is equal to {grams:.2f} grams.")

        elif option == "Grams to Moles":
            grams = st.number_input("Enter Grams:")
            molar_mass = st.number_input("Enter Molar Mass (g/mol):")
            if st.button("Convert"):
                moles = grams / molar_mass
                st.write(f"{grams} grams is equal to {moles:.2f} moles.")

        elif option == "Molarity Calculation":
            moles = st.number_input("Enter Moles of Solute:")
            volume = st.number_input("Enter Volume of Solution (liters):")
            if st.button("Calculate Molarity"):
                molarity = moles / volume
                st.write(f"The molarity of the solution is {molarity:.2f} M.")

        elif option == "Liters to Moles":
            liters = st.number_input("Enter Volume in Liters:")
            molarity = st.number_input("Enter Molarity (mol/L):")
            if st.button("Convert"):
                moles = liters * molarity
                st.write(f"{liters} liters is equal to {moles:.2f} moles.")


# Function to render the dashboard page
def dashboard():
    st.markdown(
    """
    <h1 style="font-size: 35px; font-family: 'Arial', serif; font-weight: bold;">
        Hey! This is your <span style="color: #2F4F4F;">CHEMISTRY BUDDY</span>
    </h1>
    """,
    unsafe_allow_html=True
)
    st.markdown('<p class="medium-font">Nothing is lost, nothing is created, everything is transformed.</p>', unsafe_allow_html=True)

    
    if st.button("Ask Doubts"):
        st.session_state.page = "Upload Documents" 

    # Call the unit converter function
    unit_converter()
    
    
    articles = [
        {
            "title": "Periodic Table",
            "content": "The periodic table organizes all known elements based on their atomic number and properties. It is a vital tool in chemistry for understanding the behavior of elements.",
            "image_url": "https://www.thoughtco.com/thmb/WenFixYgCRKTi-zwb5xJQ98d-vU=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/PeriodicTableWallpaper-56a12d103df78cf7726827e8.png"
        },
        {
            "title": "Physical Chemistry",
            "content": "It is a branch of chemistry concerned with interactions and transformations of materials. Unlike other branches, it deals with the principles of physics underlying all chemical interactions (e.g., gas laws)",
            "image_url": "https://images.shiksha.com/mediadata/images/articles/1522396509phpf2B7v0.jpeg"
        },
        {
            "title": "Inorganic Chemistry",
            "content": " Inorganic chemistry is concerned with the properties and behavior of inorganic compounds, which include metals, minerals, and organometallic compounds.",
            "image_url": "https://www.agproud.com/ext/resources/2023/04/27/57476-louder-minerals.jpg?t=1682621640&width=1080"
        },
        {
            "title": "Organic Chemistry",
            "content": "Organic chemistry is a subfield within chemistry that is interested in understanding organic compounds. Organic compounds are those that contain both carbon and hydrogen atoms (and sometimes other elements). Organic compounds are highly diverse and can include natural and synthetic materials.",
            "image_url": "https://learnt.io/blog/content/images/2023/10/Organic-Chemistry.jpg"
        },
        {
            "title": "Guide for IUPAC Nomenclature",
            "content": "IUPAC (International Union of Pure and Applied Chemistry) nomenclature is a standardized system for naming chemical compounds. It provides a clear and consistent method for identifying substances based on their molecular structure.",
            "image_url": "https://kpu.pressbooks.pub/app/uploads/sites/139/2020/10/FG-naming-pririty-772x1024.png"
        },     
        
    ]

    for article in articles:
        st.subheader(article["title"])
        st.write(article["content"])
        st.image(article["image_url"], width=750)  
        st.markdown("---")    


# Function to render the upload page
def upload_page():
    st.header("Ask your doubts")
    # User input for asking a question
    user_question = st.text_input("Ask any Question of chemistry")
    
    # When the user submits a question
    if user_question:
        user_input(user_question)

    st.header("Upload a document and grasp CHEMISTRY")

    # File uploader for PDF documents
    pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)
    
    # Process the documents upon submission
    if st.button("Submit & Process"):
        with st.spinner("Processing..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("Documents processed successfully!")

    # Initialize session state for storing questions and answers
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    

    # Display previous questions and their corresponding answers
    if st.session_state.qa_history:
        st.subheader("Previous Questions and Answers:")
        for idx, (question, answer) in enumerate(st.session_state.qa_history):
            st.write(f"**Q{idx + 1}:** {question}")
            st.write(f"**A{idx + 1}:** {answer}")
    
    if st.button("Back to Dashboard"):
        st.session_state.page = "Dashboard"  




# Main app logic
add_background()
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"  

if st.session_state.page == "Dashboard":
    dashboard()
else:
    upload_page()
