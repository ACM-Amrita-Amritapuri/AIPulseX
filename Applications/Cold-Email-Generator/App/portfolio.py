import os
import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self):
        # Dynamically set the file path to the CSV file
        self.file_path = os.path.join(os.path.dirname(__file__), "resource/my_portfolio.csv")

        # Load the CSV data
        self.data = pd.read_csv(self.file_path)

        # Set up the ChromaDB client
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(documents=row["Techstack"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])

    def query_links(self, skills):
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])
