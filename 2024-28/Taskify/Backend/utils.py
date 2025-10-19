import warnings
import os
import sys
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import re
import uuid
import datetime
import json 

# Comprehensive warning suppression
warnings.filterwarnings('ignore')
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)



load_dotenv()

# Embedding model, llm, vector store

embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
# Use a valid Groq model id; fall back to Gemini at runtime if Groq call fails
helper_llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), temperature=0.3)
main_llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
vstore = PineconeVectorStore(index_name=os.getenv('INDEX_NAME'),embedding=embedding_model)



def validate_username(username):
    
    if not username:
        return False,"Username is required"
    if len(username)<5 or len(username)>20:
        return False,"Username must be between 5 and 20 characters"
    if not username.isidentifier():
        return False,"Username must contain only letters,numbers and underscores"
    return True,"valid username"

def validate_password(password):
    
    if not password:
        return False,"Password is required"
    if len(password)<8:
        return False,"Password should be atleast 8 characters"
    if not any(c.islower() for c in password):
        return False,"Password must contain atleast 1 lowercase character"
    if not any(c.isupper() for c in password):
        return False,"Password must contain atleast 1 uppercase character"
    if not any(c.isdigit() for c in password):
        return False,"Password must contain atleast 1 digit"
    
    special_chars=r"!@#$%^&*()-_+=<>?/{}~|"
    if not any(c in special_chars for c in password):
        return False,"Password must contain atleast 1 special character"
    return True,"Password accepted" 

# Adding doc processing functions 

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace("–", "-").replace("—", "-")
    return text.strip()

def process_doc(file_path, doc_type, username=None):
    pages = []
    if doc_type == "pdf":
        loader = PyPDFLoader(file_path=file_path)
        for page in loader.lazy_load():
            doc = clean_text(page.page_content)
            pages.append(Document(page_content=doc,metadata=page.metadata))
    elif doc_type == "docx":
        loader = Docx2txtLoader(file_path=file_path)
        page = loader.load()[0]
        doc = clean_text(page.page_content)
        pages.append(Document(page_content=doc,metadata=page.metadata))
    try:
        # Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(pages)

        # Useful for the metadata of the embeddings
        batch_id = str(uuid.uuid4())
        upload_time = datetime.datetime.utcnow().isoformat()

        for idx, chunk in enumerate(chunks):
            chunk.metadata.update({
                "source_file": os.path.basename(file_path),
                "page_number": idx + 1,
                "doc_type": doc_type,
                "upload_batch_id": batch_id,
                "upload_time": upload_time,
                "username": username or "unknown"  # Add username to metadata
            })


        # Using pinecone to store the embeddings
        vstore.add_documents(chunks)

        return True,"succes"

    except Exception as e:
        print(e)
        return False,e 


def get_user_documents(username):
    """Retrieve all documents uploaded by a specific user from Pinecone."""
    try:
        # Use the existing vector store to query
        # Create a simple query to retrieve documents with username filter
        search_results = vstore.similarity_search(
            query="document",  # Simple query
            k=1000,  # Get up to 1000 results
            filter={"username": username}
        )
        
        # Extract unique documents by batch_id
        docs_dict = {}
        for doc in search_results:
            batch_id = doc.metadata.get('upload_batch_id')
            if batch_id and batch_id not in docs_dict:
                docs_dict[batch_id] = {
                    'filename': doc.metadata.get('source_file', 'Unknown'),
                    'doc_type': doc.metadata.get('doc_type', 'unknown'),
                    'upload_time': doc.metadata.get('upload_time', 'Unknown'),
                    'batch_id': batch_id,
                    'username': doc.metadata.get('username', 'Unknown')
                }
        
        print(f"Found {len(docs_dict)} documents for user {username}")
        return list(docs_dict.values())
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
        return []





# Helper functions for schedule generation 

def llm_text(prompt: str) -> str:
    """Invoke helper_llm, falling back to main_llm on error, and return text content."""
    try:
        res = helper_llm.invoke(prompt)
        # Some LangChain chat models return .content, others raw text
        return str(getattr(res, 'content', res) or "")
    except Exception as e:
        print(f"[llm_text] Groq invoke failed, falling back to Gemini: {e}")
        try:
            res = main_llm.invoke(prompt)
            return str(getattr(res, 'content', res) or "")
        except Exception as e2:
            print(f"[llm_text] Fallback invoke failed: {e2}")
            return ""


def pre_retrieval(user_input):
    query_analysis_prompt = f"""You are an intelligent schedule analysis assistant. Analyze the user's request to understand their EXACT needs and preferences.

User Input: "{user_input}"

Extract and infer the following information with HIGH precision:

1. **key_terms**: Extract 5-10 specific keywords/phrases from their request (include technical terms, activities, goals)
2. **intent**: Primary purpose - work, study, fitness, personal_development, meeting, creative_work, or mixed
3. **time_preference**: Preferred time of day - morning (6-12), afternoon (12-17), evening (17-21), night (21-24), or flexible
4. **priority_focus**: What matters most - productivity, learning, health, balance, creativity, or deadline_driven
5. **duration_hint**: Time commitment - short (<2hrs), medium (2-4hrs), long (4-8hrs), full_day (8+hrs), or unspecified
6. **context_type**: Document categories needed - technical_docs, learning_materials, fitness_plans, personal_notes, project_docs, or general
7. **implicit_requirements**: Infer unstated needs (e.g., "study ML" implies need for breaks, deep focus time)
8. **success_metrics**: How to measure success (tasks completed, skills learned, milestones reached)
9. **constraints**: Time limits, energy levels, dependencies, deadlines mentioned
10. **related_concepts**: Broader topics that might appear in their documents (e.g., "Python coding" → programming, algorithms, debugging)

IMPORTANT: Return ONLY a valid JSON object, no markdown, no explanations.

JSON:"""

    try:
        analysis_response_text = llm_text(query_analysis_prompt)
        try:
            analysis_response = json.loads(analysis_response_text)  # type: ignore
        except json.JSONDecodeError:
            analysis_response = {
                'key_terms': ['work', 'schedule', 'plan'],
                'intent': 'general',
                'time_preference': 'any',
                'priority_focus': 'productivity',
                'duration_hint': 'flexible',
                'context_type': 'general',
                'implicit_requirements': [],
                'success_metrics': ['completion'],
                'constraints': [],
                'related_concepts': []
            }

        search_query_prompt = f"""You are a document retrieval expert. Create a HIGHLY targeted search query to find the most relevant information from the user's uploaded documents.

**User's Original Request**: "{user_input}"

**Extracted Context**:
- Primary Intent: {analysis_response.get('intent', 'general')}
- Priority Focus: {analysis_response.get('priority_focus', 'productivity')}
- Time Preference: {analysis_response.get('time_preference', 'any')}
- Key Terms: {', '.join(analysis_response.get('key_terms', [])) if isinstance(analysis_response.get('key_terms', []), list) else str(analysis_response.get('key_terms', ''))}
- Document Type Needed: {analysis_response.get('context_type', 'general')}
- Implicit Needs: {', '.join(analysis_response.get('implicit_requirements', [])) if isinstance(analysis_response.get('implicit_requirements', []), list) else str(analysis_response.get('implicit_requirements', ''))}
- Related Topics: {', '.join(analysis_response.get('related_concepts', [])) if isinstance(analysis_response.get('related_concepts', []), list) else str(analysis_response.get('related_concepts', ''))}

**Task**: Craft a concise search query (2-4 sentences) that:
✓ Combines the MOST relevant key terms and concepts
✓ Focuses on {analysis_response.get('intent', 'general')} and {analysis_response.get('priority_focus', 'productivity')}
✓ Uses natural language that matches how information appears in documents
✓ Balances specificity (to find exact topics) with breadth (to capture related context)

**Return ONLY the optimized search query, no labels or explanations:**"""

        optimized_query = llm_text(search_query_prompt) or user_input
        return optimized_query, analysis_response
    except Exception as e:
        print(f"Error in pre-retrieval processing: {e}")
        return "", {}
    
    
# Retrieving documents
def doc_retrieval(query,analysis_data):
    
    try:
        retriver=vstore.as_retriever(search_kwargs={"k":5}) 
        
        docs=retriver.get_relevant_documents(query=query)
        
        
        # Scoring each document for relevance 
        # This score will be useful while reranking
        
        scored_docs=[]
        
        for doc in docs:
            
            scoring_prompt = f"""You are a document relevance expert. Rate how useful this document chunk is for creating a personalized schedule.

**User's Schedule Needs**:
- Intent: {analysis_data['intent']}
- Priority: {analysis_data['priority_focus']}
- Context Type: {analysis_data['context_type']}
- Looking For: {', '.join(analysis_data['key_terms'][:5]) if isinstance(analysis_data.get('key_terms', []), list) else str(analysis_data.get('key_terms', ''))}

**Document Excerpt**:
{doc.page_content[:600]}

**Scoring Criteria** (1-10):
- 9-10: Directly contains tasks, timelines, or specific activities mentioned by user
- 7-8: Highly relevant context (goals, milestones, priorities that inform scheduling)
- 5-6: Moderately relevant (general information about topics user mentioned)
- 3-4: Loosely related (same domain but not directly applicable)
- 1-2: Irrelevant or off-topic

**Return ONLY a single number (1-10):**"""
        
        try:
            relevance_text = llm_text(scoring_prompt)
            score_match=re.search(r'\d+', relevance_text) # type: ignore
            score=int(score_match.group()) if score_match else 5 
        
        except:
            score=5
            
        # Traditional scoring 
        
        content=doc.page_content.lower()
        traditional_score=0
        
        
        # Score based on key terms 
        for term in analysis_data['key_terms']:
            if term in content:
                traditional_score+=1
        
        # Based on intent relevance
        
        if analysis_data['intent'] in content:
            traditional_score+=2
            
        # Based on schedule related stuff
        
        if any(word in content for word in ['schedule', 'plan', 'time', 'task', 'routine', 'productivity']):
                traditional_score += 2
                
        # Getting final score 
        
        final_score=(score*0.5)+(traditional_score*0.5)
        
        scored_docs.append({
                'document': doc,
                'score': final_score,
                'llm_score': score,
                'traditional_score': traditional_score,
                'content': doc.page_content,
                'metadata': doc.metadata
            })

        
        return scored_docs
    
    
    except Exception as e:
        print(f"Error in document retrieval: {e}")
        return [] 
        

# Reranking documents

def reranking(scored_docs,analysis_data,top_k=5):
    
    try:
        if not scored_docs:
            return []
        
        rerank_prompt = f"""You are a context prioritization expert. Re-rank these document chunks to identify the MOST useful information for creating a personalized schedule.

**User's Schedule Requirements**:
- Primary Goal: {analysis_data['intent']}
- Focus Area: {analysis_data['priority_focus']}
- Preferred Time: {analysis_data['time_preference']}
- Key Terms: {', '.join(analysis_data.get('key_terms', [])[:5]) if isinstance(analysis_data.get('key_terms', []), list) else str(analysis_data.get('key_terms', ''))}

**Document Chunks** (with initial scores):
"""
        
        for i,doc in enumerate(scored_docs[:10]):  # Limit to top 10 for better LLM focus
            rerank_prompt+=f"\n[{i+1}] Score: {doc['score']:.2f}\nContent: {doc['content'][:250]}...\n"
            
            
        rerank_prompt+="""
**Task**: Rank these documents from MOST to LEAST relevant for schedule creation.
- Prioritize chunks with specific tasks, timings, activities, or deadlines
- Value concrete information over general descriptions
- Consider user's intent and priorities

**Return ONLY the ranking numbers separated by commas** (e.g., "3,1,5,2,4"):"""

        try:
            response=llm_text(rerank_prompt)
            
            # Parse the rankings
            
            rankings=[int(x.strip()) -1 for x in response.split(",") if x.strip().isdigit()] #type: ignore
            
            reranked_docs=[]
            
            for rank in rankings:
                if 0 <= rank < len(scored_docs):
                    reranked_docs.append(scored_docs[rank]) 
                    
            if not reranked_docs:
                reranked_docs = sorted(scored_docs, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            print("llm  reranking failure")
        
            reranked_docs = sorted(scored_docs, key=lambda x: x['score'], reverse=True) 
        
        top_docs=reranked_docs[:top_k]
        context_text = "\n\n".join([sd['content'] for sd in top_docs]) 
        return context_text
    
    except Exception as e:
        print(f"Error in reranking: {e}")
        top_docs=sorted(scored_docs, key=lambda x: x['score'], reverse=True)[:top_k] 
        context_text = "\n\n".join([sd['content'] for sd in top_docs]) 
        return context_text
    
    
    
# Schedule generation prompt

def process_schedule(user_query,context):
    # Get the directory where this file (utils.py) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    examples_path = os.path.join(current_dir, "examples.txt")
    
    print(f"\n[process_schedule] User query: {user_query}")
    print(f"[process_schedule] Context length: {len(context) if context else 0}")
    
    with open(examples_path,'r') as f:
        examples_json = f.read()
        try:
            examples = json.loads(examples_json)  # Parse JSON first
            print(f"[process_schedule] Loaded {len(examples)} examples")
        except json.JSONDecodeError as e:
            print(f"[process_schedule] Error parsing examples.txt: {e}")
            examples = []  # Fallback to empty list if parsing fails
        
        examples_text = []
        for ex in examples:
            examples_text.append(
                f"Example Input: {ex.get('input', '')}"
                f"\nExample Context: {ex.get('context', '')}"
                f"\nExample JSON Output: {json.dumps(ex.get('output', {}), ensure_ascii=False, indent=2)}"
            ) 
        
        schedule_gen_prompt= f"""You are an expert curriculum designer and learning path architect. Create a COMPREHENSIVE, WEEK-BY-WEEK learning schedule that breaks down the entire roadmap into a structured multi-week plan.

════════════════════════════════════════════════════════════════
📋 USER'S REQUEST & TIME COMMITMENT:
{user_query}

📚 COMPLETE ROADMAP FROM USER'S DOCUMENTS:
{context if context else 'No specific roadmap found - create a general learning plan based on the request.'}

════════════════════════════════════════════════════════════════
📖 EXAMPLES OF WELL-STRUCTURED WEEK-WISE SCHEDULES:

{chr(10).join(examples_text)}

════════════════════════════════════════════════════════════════
🎯 YOUR TASK - CREATE A DETAILED MULTI-WEEK SCHEDULE:

**CRITICAL UNDERSTANDING**:
- This is NOT a single-day schedule
- This is a COMPLETE LEARNING PATH spanning multiple weeks
- Break down the ENTIRE roadmap into weekly chunks
- Each week focuses on specific topics from the roadmap
- Each day within a week has theory + practice sessions

**ANALYZE USER'S TIME COMMITMENT**:
1. Extract daily time available (e.g., "1 hour per day" = 60 min)
2. Extract total duration (e.g., "4 weeks", "2 months", or calculate based on roadmap complexity)
3. If duration not specified, calculate realistic timeline based on roadmap content

**STRUCTURE YOUR SCHEDULE**:

```json
{{
  "title": "Descriptive title for the complete learning plan",
  "description": "What the user will achieve by completing this schedule",
  "duration_per_day": <minutes per day user can commit>,
  "total_weeks": <number of weeks needed>,
  "total_duration": <total minutes across all weeks>,
  "theme": "technical_learning|web_development|data_science|fitness|personal_development",
  "productivity_score": <0-100 based on schedule quality>,
  "weeks": [
    {{
      "week_number": 1,
      "week_title": "Descriptive title for this week",
      "week_goal": "What user will master this week",
      "topics": ["Topic 1 from roadmap", "Topic 2", "Topic 3", "Topic 4"],
      "daily_sessions": [
        {{
          "day": "Monday",
          "topic": "Specific topic for this day",
          "theory": "X min - What theoretical concepts to cover",
          "practice": "Y min - What hands-on practice to do",
          "duration": <total minutes for the day>
        }},
        {{
          "day": "Tuesday",
          "topic": "Next topic",
          "theory": "...",
          "practice": "...",
          "duration": <minutes>
        }},
        // ... Wednesday, Thursday, Friday (or all 7 days if needed)
      ]
    }},
    {{
      "week_number": 2,
      "week_title": "Next phase title",
      "week_goal": "...",
      "topics": [...],
      "daily_sessions": [...]
    }}
    // ... continue for all weeks
  ]
}}
```

**REQUIREMENTS FOR EACH WEEK**:
1. **Week Title**: Clear, descriptive (e.g., "RAG Fundamentals & Architecture")
2. **Week Goal**: Specific learning outcome (e.g., "Understand core concepts and system architecture")
3. **Topics**: 3-5 specific topics from roadmap to cover this week
4. **Daily Sessions**: 5-7 days per week (Monday-Friday minimum)
   - Each day focuses on ONE specific topic
   - Balance theory (30-40% of time) and practice (60-70% of time)
   - Theory: Reading, watching videos, understanding concepts
   - Practice: Coding, building projects, hands-on exercises

**PROGRESSION STRATEGY**:
- Week 1: Fundamentals and foundational concepts
- Week 2-3: Core skills and intermediate techniques
- Week 4+: Advanced topics and real-world projects
- Final Week: Integration, deployment, and capstone project

**CALCULATE REALISTIC TIMELINE**:
- For complex roadmaps (e.g., RAG, Full-Stack): 4-12 weeks
- For focused topics (e.g., specific framework): 2-4 weeks
- For comprehensive learning (e.g., ML from scratch): 8-16 weeks
- Ensure: total_duration = duration_per_day × 5 days × total_weeks (minimum)

⚠️ CRITICAL REQUIREMENTS:
- Return ONLY valid JSON - NO markdown code blocks (no backticks), NO explanations
- Start your response immediately with the opening curly brace
- Cover the ENTIRE roadmap from the user's documents
- Each week must have 5+ daily sessions
- Each daily session must have both theory and practice
- Theory + practice duration must equal the daily time commitment
- Topics must be pulled from the roadmap context provided
- Progression must be logical (basics → intermediate → advanced)

⛔ DO NOT wrap output in markdown code blocks
✅ Return raw JSON starting with opening brace
✅ Include ALL weeks needed to complete the roadmap

JSON OUTPUT:
    """
    
    schedule_draft=main_llm.invoke(schedule_gen_prompt).content 
    print(f"[process_schedule] Raw LLM response length: {len(schedule_draft) if schedule_draft else 0}")
    print(f"[process_schedule] Raw LLM response preview: {str(schedule_draft)[:500] if schedule_draft else 'EMPTY'}...")
    
    # Extract JSON from markdown code blocks if present
    if schedule_draft:
        schedule_draft = str(schedule_draft).strip()
        # Remove markdown code blocks
        if schedule_draft.startswith('```'):
            # Remove opening ```json or ```
            schedule_draft = re.sub(r'^```(?:json)?\s*', '', schedule_draft)
            # Remove closing ```
            schedule_draft = re.sub(r'\s*```$', '', schedule_draft)
            schedule_draft = schedule_draft.strip()
        print(f"[process_schedule] Cleaned JSON preview: {schedule_draft[:300]}...")
    
    # Post Schedule gen validation checks 
    
    try:
        schedule_draft=json.loads(schedule_draft) #type: ignore
        print(f"[process_schedule] Successfully parsed JSON schedule")
        return schedule_draft
    except json.JSONDecodeError as e:
        print(f"[process_schedule] JSON parsing failed: {e}")
        print(f"[process_schedule] Attempting to fix malformed JSON...")
        fixing_prompt= f"""The following text should be a valid schedule JSON. Fix and return ONLY valid JSON.

⚠️ CRITICAL: Do NOT wrap the JSON in markdown code blocks. Do NOT use ```json or ```. Return ONLY the raw JSON object.

---
{schedule_draft}
---

Ensure keys: title, description, tasks[], total_duration, break_time, theme, productivity_score.
Each task MUST have: title, description, duration (minutes), priority in [high, medium, low], start_time HH:MM, end_time HH:MM, category in [work, study, fitness, personal, meeting, break].

Return the corrected JSON immediately, with no markdown formatting:
"""     
        fixed_schedule = llm_text(fixing_prompt)
        
        # Extract JSON from markdown if fixing prompt also returned markdown
        if fixed_schedule:
            fixed_schedule = str(fixed_schedule).strip()
            if fixed_schedule.startswith('```'):
                fixed_schedule = re.sub(r'^```(?:json)?\s*', '', fixed_schedule)
                fixed_schedule = re.sub(r'\s*```$', '', fixed_schedule)
                fixed_schedule = fixed_schedule.strip()
        
        try:
            return json.loads(fixed_schedule)  # type: ignore
        except json.JSONDecodeError:
            return {
                "title": "AI Generated Schedule",
                "description": "Schedule created based on your input",
                "tasks": [],
                "total_duration": 0,
                "break_time": 0,
                "theme": "daily",
                "productivity_score": 0
            }
            
            

            
def get_context(query):
    print(f"\n[get_context] Starting with query: {query}")
    optimized_query,analysis_response=pre_retrieval(user_input=query) #type: ignore
    print(f"[get_context] Optimized query: {optimized_query}")
    
    docs=doc_retrieval(optimized_query,analysis_response) #type: ignore
    print(f"[get_context] Docs retrieved (type): {type(docs)}, length: {len(docs) if docs else 0}")
    
    context=reranking(docs,analysis_response) #type: ignore
    print(f"[get_context] Context after reranking (length): {len(context) if context else 0}")
    
    return context,analysis_response

