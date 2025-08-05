
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)
from fastapi import FastAPI, HTTPException , File, UploadFile
import shutil
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from docx2pdf import convert
from org.doc_loader import load_and_chunk_pdf , load_and_chunk_excel ,load_and_chunk_ppt
from org.embeddings import embed_and_upsert, model, index
from org.matching import query_pinecone
from org.model import build_prompt, query_mistral_local
from org.pptconversion import ppt_to_pptx_soffice
app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class AnswerChunk(BaseModel):
    text: str     
    source: str             
    score: float            
    # --- PDF-only ---
    page: Optional[int] = None       # 1-based page number
    # --- PowerPoint-only ---
    slide: Optional[int] = None      # 1-based slide number
    # --- Excel-only ---
    sheet: Optional[str] = None      # sheet name
    start_row: Optional[int] = None  # 1-based first row in chunk
    end_row: Optional[int] = None    # 1-based last row in chunk

class QueryResponse(BaseModel):
    answer: str
    references: List[AnswerChunk]


app = FastAPI()
UPLOAD_DIR = "./uploaded_docs"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    print(save_path)

    # Save file to disk
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = os.path.splitext(save_path)[1].lower()
    flag = 0
    if ext == ".ppt":
        try:
            save_path = ppt_to_pptx_soffice(save_path)
            ext = ".pptx"
            os.remove(os.path.splitext(save_path)[0] + ".ppt")
        except Exception as e:
            raise HTTPException(422, f"PPT conversion failed: {e}")
    if ext in ['.doc', '.docx']:
        convert(save_path, UPLOAD_DIR)
        pdf_path = os.path.splitext(save_path)[0] + ".pdf"
        flag = 1
    else:
        pdf_path = save_path
    filename2 = os.path.basename(pdf_path)

    if ext in ['.xlsx', '.xls']:
        excel_chunks, excel_metadata = load_and_chunk_excel(save_path)
        embed_and_upsert(excel_chunks, excel_metadata)
    elif ext == '.pptx':
        ppt_chunks, ppt_meta = load_and_chunk_ppt(save_path)
        embed_and_upsert(ppt_chunks, ppt_meta)    
    else:    
        docx_chunks, docx_metadata = load_and_chunk_pdf(pdf_path)
        embed_and_upsert(docx_chunks, docx_metadata)
    if flag:
        os.remove(save_path)

    return {"message": f"{file.filename} uploaded!"}

@app.get("/files/")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    try:
        
        top_chunks = query_pinecone(req.question, top_k=req.top_k)
        if not top_chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found.")

        prompt = build_prompt(top_chunks, req.question)

        answer = query_mistral_local(prompt)
        
        # Step 4: Format references for response
        references = []
        for chunk in top_chunks:
            references.append(
                AnswerChunk(
                    text      = chunk.get("text", ""),     # or meta.get("text", "")
                    source    = chunk.get("source", "N/A"),
                    score     = chunk.get("score", 0.0),
                    page      = chunk.get("page"),
                    slide     = chunk.get("slide"),
                    sheet     = chunk.get("sheet"),
                    start_row = chunk.get("start_row"),
                    end_row   = chunk.get("end_row")
                )
            )
        
        return QueryResponse(answer=answer, references=references)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/files/{filename}")
def delete_file(filename: str):
    save_path = os.path.join(UPLOAD_DIR, filename)
    ext = os.path.splitext(save_path)[1].lower()
    if ext in ['.xlsx' , 'xls']:
        _, docx_metadata = load_and_chunk_excel(save_path)
    elif ext in ['.pptx']:
        _, docx_metadata = load_and_chunk_ppt(save_path)
    else:    
       _, docx_metadata = load_and_chunk_pdf(save_path)
    
    # Build vector IDs to delete (same convention as upsert)
    vec_ids_to_delete = [
        f"{filename}_{i}"
        for i, meta in enumerate(docx_metadata)
        if meta['source'] == filename
    ]
    print(f"Deleting {len(vec_ids_to_delete)} vectors for '{filename}'...")

    if not vec_ids_to_delete:
        return {"message":"no ids to delete"}

    if vec_ids_to_delete:
        print(vec_ids_to_delete)
        index.delete(ids=vec_ids_to_delete)
        print("Deletion complete.")
    else:
        print("No matching vectors found to delete.")
    save_path = os.path.join(UPLOAD_DIR, filename)    
    os.remove(save_path)

    return {"status": "ok"}


if __name__ == "__main__":
    # Run with: uvicorn app:app --reload
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
