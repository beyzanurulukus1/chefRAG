import os
import json
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings # Değişen kısım
from langchain_chroma import Chroma

def load_and_process_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Artık kota derdimiz yok, tüm veriyi (veya istediğin kadarını) alabilirsin
    df = pd.DataFrame(data).head(500) 
    
    documents = []
    for _, row in df.iterrows():
        malzemeler_listesi = [f"{m.get('miktar', '')} {m.get('birim', '')} {m.get('isim', '')}".strip() for m in row['malzemeler']]
        malzemeler = ", ".join(malzemeler_listesi)
        yapilis = " ".join(row['yapilis_adimlari'])
        content = f"Yemek: {row['tarif_adi']}\nMalzemeler: {malzemeler}\nTarif: {yapilis}"
        doc = Document(page_content=content, metadata={"baslik": row['tarif_adi']})
        documents.append(doc)
    return documents

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(documents)

def ingest_to_vector_db(chunks):
    # TEKNİK ANLATIM: Açık kaynaklı bir embedding modeli kullanıyoruz (all-MiniLM-L6-v2)
    # Bu sayede API limitlerine takılmadan yüksek performanslı vektörleştirme sağlıyoruz.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists("./chroma_db"):
        import shutil
        shutil.rmtree("./chroma_db")

    print(f"Toplam {len(chunks)} parça yerel olarak vektörleştiriliyor...")
    
    # Yerel çalıştığı için batch/sleep işlemine gerek kalmadı!
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print("Vektör veritabanı hazır! Hiçbir API kotası kullanılmadı.")

if __name__ == "__main__":
    docs = load_and_process_data('tarifler.json')
    chunks = split_documents(docs)
    ingest_to_vector_db(chunks)