import logging
import json
import time
import hashlib
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
import openai
import yaml

# --- A3 concise KB constants and cache ---
_A3_SNIPPETS_CACHE: Optional[List[Dict[str, Any]]] = None
_A3_SNIPPETS_PATH: Optional[str] = None
_A3_SENT_SPLIT_REGEX = re.compile(r'[.?!]+')
_A3_MAX_LEN = 120
_A3_MAX_SENTS = 2
_A3_ALLOWED_PERSONAS = {"D", "I", "S", "C"}

def _a3_trim_to_caps(text: str, max_len: int = _A3_MAX_LEN, max_sents: int = _A3_MAX_SENTS) -> str:
    """
    Trim text to <= max_sents sentences and <= max_len chars, preferring sentence boundaries.
    """
    if not text:
        return text
    pieces = _A3_SENT_SPLIT_REGEX.split(text)
    kept = []
    for piece in pieces:
        p = piece.strip()
        if p:
            kept.append(p)
            if len(kept) >= max_sents:
                break
    candidate = ". ".join(kept) if kept else text.strip()
    if kept and text.strip().endswith(tuple(".?!")):
        candidate = candidate.rstrip() + "."
    if len(candidate) <= max_len:
        return candidate
    return candidate[:max_len].rstrip()

def _a3_sentence_count(text: str) -> int:
    segs = [s for s in _A3_SENT_SPLIT_REGEX.split(text) if s.strip()]
    return len(segs)

def _a3_load_snippets_once(path: str = "data/concise_snippets.json") -> List[Dict[str, Any]]:
    """
    Load concise snippets from JSON once (cache-once pattern). Supports either:
      - array of snippet dicts with 'id','text','tags'
      - array of strings (legacy), which will be transformed into minimal snippets

    Note: If the cache is already populated, return it regardless of the requested path.
    Tests seed the cache by calling this with their fixture path first.
    """
    global _A3_SNIPPETS_CACHE, _A3_SNIPPETS_PATH
    if _A3_SNIPPETS_CACHE is not None and _A3_SNIPPETS_PATH == path:
        return _A3_SNIPPETS_CACHE

    try:
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            _A3_SNIPPETS_CACHE = data
            _A3_SNIPPETS_PATH = path
        elif isinstance(data, list) and all(isinstance(x, str) for x in data):
            # Transform legacy to minimal persona-agnostic KB_QA/general
            transformed: List[Dict[str, Any]] = []
            for i, txt in enumerate(data):
                transformed.append({
                    "id": f"chunk_{i}",
                    "text": _a3_trim_to_caps(str(txt or "")),
                    "tags": {"node_id": "KB_QA", "topic": "general", "persona": None}
                })
            _A3_SNIPPETS_CACHE = transformed
            _A3_SNIPPETS_PATH = path
        else:
            logging.warning("A3 loader: Unsupported JSON structure for concise snippets; using empty set")
            _A3_SNIPPETS_CACHE = []
            _A3_SNIPPETS_PATH = path
            _A3_SNIPPETS_PATH = path
    except Exception as e:
        logging.error(f"A3 loader: Failed to load snippets: {e}", exc_info=False)
        _A3_SNIPPETS_CACHE = []

    return _A3_SNIPPETS_CACHE

def _a3_stable_hash(seed_keys: Optional[Tuple[Any, ...]]) -> int:
    """
    FNV1a-32 hash for good distribution of rotating snippets.
    """
    if not seed_keys:
        return 0
    # FNV1a-32 constants
    h = 0x811c9dc5
    for byte in ("||".join(map(str, seed_keys))).encode("utf-8"):
        h ^= byte
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h

def _load_ext_config(path: str = "generative_handler_config.yml") -> Dict[str, Any]:
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data or {}
    except Exception:
        return {}

# Strict internal implementation (positional-friendly)
def _strict_get_concise_snippet(node_id: str,
                                 topic: str,
                                 persona: Optional[str],
                                 max_len: int = _A3_MAX_LEN,
                                 max_sents: int = _A3_MAX_SENTS,
                                 seed_keys: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns a dict { 'id': str, 'text': str, 'tags': {...} } or None.

    Deterministic fallback order:
      a) node_id + topic + persona
      b) node_id + topic + persona=None
      c) topic-only + persona=None (across nodes)

    Enforces caps (<= max_len chars and <= max_sents sentences).
    """
    snippets = _a3_load_snippets_once()

    # Build candidate pools
    cands_a: List[Dict[str, Any]] = []
    cands_b: List[Dict[str, Any]] = []
    cands_c: List[Dict[str, Any]] = []
    for sn in snippets:
        tags = sn.get("tags", {})
        nid = tags.get("node_id")
        tpc = tags.get("topic")
        per = tags.get("persona", None)
        if nid == node_id and tpc == topic and persona is not None and per == persona:
            cands_a.append(sn)
        elif nid == node_id and tpc == topic and per is None:
            cands_b.append(sn)
        elif tpc == topic and per is None:
            cands_c.append(sn)

    pool = cands_a or cands_b or cands_c
    selected_level = "a" if cands_a else ("b" if cands_b else ("c" if cands_c else None))

    if not pool:
        logging.info(json.dumps({
            "a3_kb_retrieval": True,
            "node_id": node_id,
            "topic": topic,
            "persona": persona if persona in _A3_ALLOWED_PERSONAS else (persona if persona is None else "other"),
            "selected_id": None,
            "candidates": 0,
            "seed_hash": _a3_stable_hash(seed_keys) if seed_keys else None,
            "fallback_level": None
        }))
        return None

    idx = 0
    if seed_keys and len(pool) > 1:
        idx = _a3_stable_hash(seed_keys) % len(pool)
    selected = pool[idx]

    text = selected.get("text") or ""
    trimmed = _a3_trim_to_caps(text, max_len=max_len, max_sents=max_sents)
    result = {"id": selected.get("id"), "text": trimmed, "tags": selected.get("tags", {})}

    logging.info(json.dumps({
        "a3_kb_retrieval": True,
        "node_id": node_id,
        "topic": topic,
        "persona": persona if persona in _A3_ALLOWED_PERSONAS else (persona if persona is None else "other"),
        "selected_id": result["id"],
        "candidates": len(pool),
        "seed_hash": _a3_stable_hash(seed_keys) if seed_keys else None,
        "fallback_level": selected_level
    }))
    return result

class KBProcessor:
    def __init__(self, pdf_path: str = "data/dan_in_ippei_and_company_info.pdf", openai_api_key: str = None):
        """
        Initialize the KB processor with pre-loaded embeddings.
        
        Args:
            pdf_path: Path to the PDF document to process
            openai_api_key: OpenAI API key for embeddings and LLM
        """
        self.pdf_path = pdf_path
        self.vector_db = None
        self.doc_chunks = []
        self.embeddings = None
        self.llm = None
        self.cache = {}
        self.metrics = {
            'query_count': 0,
            'total_query_time': 0,
            'search_time': 0,
            'response_generation_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        # Persistent cache file for KB responses
        self.cache_file = "data/kb_cache.json"
        # Attempt to load persistent cache (best-effort)
        try:
            self._load_cache()
        except Exception:
            pass
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        
        # In a test environment, do not initialize the KB to avoid API calls
        if os.environ.get("TESTING") == "true":
            logging.warning("KBProcessor: TESTING environment detected. Skipping KB initialization.")
            return

        logging.info("KBProcessor: Initializing KB...")
        self._initialize_kb()
    
    def _initialize_kb(self):
        """
        Initialize the knowledge base with pre-processed embeddings.
        """
        try:
            logging.info("KBProcessor: Initializing embeddings model...")
            # Initialize embeddings model
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            logging.info("KBProcessor: OpenAIEmbeddings initialized.")
            
            logging.info("KBProcessor: Initializing LLM for response generation...")
            # Initialize LLM for response generation
            self.llm = openai.OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
            logging.info(f"KBProcessor: LLM initialized: {self.llm is not None}")
            
            # Try to load pre-built FAISS index
            try:
                index_file = "data/kb_index.faiss"
                chunks_file = "data/doc_chunks.json"
                
                # Check if files exist before trying to load them
                if not os.path.exists(index_file):
                    logging.info(f"KBProcessor: FAISS index file not found: {index_file}")
                    raise FileNotFoundError(f"FAISS index file not found: {index_file}")
                
                if not os.path.exists(chunks_file):
                    logging.info(f"KBProcessor: Document chunks file not found: {chunks_file}")
                    raise FileNotFoundError(f"Document chunks file not found: {chunks_file}")
                
                # Load the FAISS index using Langchain's FAISS.load_local method
                from langchain_community.docstore.in_memory import InMemoryDocstore
                from langchain_core.documents import Document
                
                # Load the raw FAISS index
                index = faiss.read_index(index_file)
                
                # Load document chunks
                with open(chunks_file, "r") as f:
                    self.doc_chunks = json.load(f)
                
                # Create Document objects from chunks
                documents = [Document(page_content=chunk) for chunk in self.doc_chunks]
                
                # Create a docstore
                docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})
                
                # Create index_to_docstore_id mapping
                index_to_docstore_id = {i: str(i) for i in range(len(documents))}
                
                # Create the FAISS vector store with the loaded index
                self.vector_db = FAISS(
                    embedding_function=self.embeddings,
                    index=index,
                    docstore=docstore,
                    index_to_docstore_id=index_to_docstore_id
                )
                
                logging.info("KBProcessor: Loaded pre-built KB index successfully.")
            except (FileNotFoundError, RuntimeError) as e:
                # If pre-built index doesn't exist or can't be loaded, create it
                logging.info(f"KBProcessor: Pre-built KB index not found or could not be loaded: {e}. Attempting to build new index.")
                self._build_kb_index()
                
        except Exception as e:
            logging.error(f"KBProcessor: Error initializing KB: {e}", exc_info=True)
    
    def _build_kb_index(self):
        """
        Build the knowledge base index from the PDF document.
        """
        try:
            # Check if PDF file exists
            if not os.path.exists(self.pdf_path):
                logging.warning(f"Knowledge base PDF not found at {self.pdf_path}. KB functionality will be disabled.")
                return
            
            # Create data directory if it doesn't exist
            data_dir = os.path.dirname(self.pdf_path)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            # Load and process the PDF
            logging.info(f"Loading PDF from {self.pdf_path}")
            loader = PyPDFLoader(self.pdf_path)
            documents = loader.load()
            
            # Split documents into chunks
            logging.info("Splitting documents into chunks")
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(documents)
            
            # Store document chunks
            self.doc_chunks = [doc.page_content for doc in docs]
            
            # Create embeddings and store in vector database
            logging.info("Creating embeddings")
            self.vector_db = FAISS.from_documents(docs, self.embeddings)
            
            # Save the index and chunks for future use
            index_file = "data/kb_index.faiss"
            chunks_file = "data/doc_chunks.json"
            
            logging.info(f"Saving vector database to {index_file}")
            faiss.write_index(self.vector_db.index, index_file)
            
            logging.info(f"Saving document chunks to {chunks_file}")
            with open(chunks_file, "w") as f:
                json.dump(self.doc_chunks, f)
                
            logging.info(f"Built KB index with {len(self.doc_chunks)} chunks")
            
        except Exception as e:
            logging.error(f"Error building KB index: {e}", exc_info=True)
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for the given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return np.array([embedding]).astype('float32')
        except Exception as e:
            logging.error(f"Error generating embedding: {e}", exc_info=True)
            # Return a zero vector as fallback
            return np.zeros((1, 1536)).astype('float32')
    
    def _get_cache_key(self, query: str) -> str:
        """
        Generate a cache key for the given query.
        
        Args:
            query: Query string
            
        Returns:
            MD5 hash of the query
        """
        return hashlib.md5(query.encode()).hexdigest()
    
    def _generate_response(self, user_query: str, relevant_chunks: List[str]) -> str:
        """
        Generate a natural language response based on relevant document chunks.
        
        Args:
            user_query: The user's question
            relevant_chunks: Relevant document chunks
            
        Returns:
            Generated response
        """
        try:
            # Combine relevant chunks
            context = "\n".join(relevant_chunks)
            
            # Create prompt for LLM
            logging.debug(f"KB_Processor._generate_response: User Query: {user_query}, Relevant Chunks: {relevant_chunks}")
            prompt = f"""
            You are a friendly and engaging assistant. Your goal is to provide concise, direct answers about a business opportunity. Avoid formal phrases like "Based on the information provided." Do NOT add follow-up questions or conversational pivots. Just provide the answer.

            Here's some context that might help:
            {context}

            Now, answer the user's question directly and conversationally. If the context doesn't contain relevant information, provide a general, engaging response about the business model.

            User Question: {user_query}

            Answer:
            """
            
            logging.debug(f"KB_Processor._generate_response: Prompt sent to LLM: {prompt}")
            
            # Generate response using LLM
            response = self.llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly and engaging assistant, focused on clear, concise, and conversational responses that encourage interaction."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=120,
                temperature=0.7
            )
            
            generated_content = response.choices[0].message.content.strip()
            logging.debug(f"KB_Processor._generate_response: Response received from LLM: {generated_content}")
            return generated_content
            
        except Exception as e:
            logging.error(f"Error generating response: {e}", exc_info=True)
            return "I can definitely help you with that! Our program offers some great benefits, and I'd love to tell you more."
    
    def _log_metrics(self):
        """
        Log performance metrics.
        """
        try:
            avg_query_time = self.metrics['total_query_time'] / self.metrics['query_count'] if self.metrics['query_count'] > 0 else 0
            cache_hit_rate = self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
            
            logging.info(f"KB Metrics - Queries: {self.metrics['query_count']}, "
                        f"Avg Time: {avg_query_time:.3f}s, "
                        f"Cache Hit Rate: {cache_hit_rate:.2%}")
        except Exception as e:
            logging.error(f"Error logging metrics: {e}", exc_info=True)

    # Persistent cache helpers
    def _load_cache(self):
        """
        Load persistent KB cache from disk if available.
        """
        try:
            path = getattr(self, "cache_file", "data/kb_cache.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.cache = json.load(f) or {}
                logging.info(f"KB cache loaded from {path} with {len(self.cache)} entries")
            else:
                self.cache = {}
        except Exception as e:
            logging.error(f"Error loading KB cache: {e}", exc_info=False)
            self.cache = {}

    def _save_cache(self):
        """
        Persist KB cache to disk.
        """
        try:
            path = getattr(self, "cache_file", "data/kb_cache.json")
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                json.dump(self.cache, f)
        except Exception as e:
            logging.error(f"Error saving KB cache: {e}", exc_info=False)
    
    def query(self, user_query: str, k: int = 2) -> str:
        """
        Query the knowledge base and generate a response.
        
        Args:
            user_query: The user's question or context
            k: Number of similar documents to retrieve
            
        Returns:
            Generated response based on relevant documents
        """
        start_time = time.time()
        self.metrics['query_count'] += 1
        
        try:
            # Check if vector database is initialized
            if self.vector_db is None:
                logging.warning("Vector database not initialized")
                return "I can help you with that. Our program has many benefits that I can tell you about."
            
            # Check cache first
            cache_key = self._get_cache_key(user_query)
            if cache_key in self.cache:
                self.metrics['cache_hits'] += 1
                cached_response = self.cache[cache_key]
                self.metrics['total_query_time'] += time.time() - start_time
                return cached_response
            
            self.metrics['cache_misses'] += 1
            
            # Search for similar documents
            search_start = time.time()
            docs = self.vector_db.similarity_search(user_query, k=k)
            self.metrics['search_time'] += time.time() - search_start
            
            # Extract content from documents
            relevant_chunks = [doc.page_content for doc in docs]
            
            # Generate response (measure time)
            response_start = time.time()
            # If LLM is not initialized, return a simple response based on chunks
            if self.llm is None:
                response = "Based on what I've learned, our program has many benefits that can help you achieve your goals. "
                response += " ".join(relevant_chunks[:2])  # Add first two chunks as context
            else:
                response = self._generate_response(user_query, relevant_chunks)

            # Normalize to envelope if feature flag enabled
            try:
                cfg = _load_ext_config()
            except Exception:
                cfg = {}
            return_envelope = False
            if isinstance(cfg, dict):
                return_envelope = cfg.get("kb_return_envelope", cfg.get("features", {}).get("kb_return_envelope", False))

            if return_envelope:
                envelope = {
                    "answer": str(response or ""),
                    "sources": [],
                    "chunks": relevant_chunks[:k] if isinstance(relevant_chunks, list) else [],
                    "model": "gpt-3.5-turbo" if self.llm is not None else "none"
                }
                response = envelope

            logging.debug(f"KBProcessor.query: returning type={type(response).__name__}, preview='{str(response)[:160]}'")
            self.metrics['response_generation_time'] += time.time() - response_start
            
            # Cache the response
            self.cache[cache_key] = response
            # Persist cache best-effort
            try:
                self._save_cache()
            except Exception:
                pass
            
            total_time = time.time() - start_time
            self.metrics['total_query_time'] += total_time
            
            # Log performance metrics periodically
            if self.metrics['query_count'] % 100 == 0:
                self._log_metrics()
            
            return response
        except Exception as e:
            logging.error(f"Error querying KB: {e}", exc_info=True)
            self.metrics['total_query_time'] += time.time() - start_time
            logging.error(f"KBProcessor: Error querying KB: {e}", exc_info=True)
            self.metrics['total_query_time'] += time.time() - start_time
            return "I can help you with that. Our program has many benefits that I can tell you about."

# Back-compat aliases for tests and legacy callers expecting persona_or_none kw

def get_concise_snippet_alias(node_id: Optional[str] = None,
                              topic: Optional[str] = None,
                              persona_or_none: Optional[str] = None,
                              seed_keys: Optional[Tuple[Any, ...]] = None,
                              max_chars: int = _A3_MAX_LEN,
                              max_sents: int = _A3_MAX_SENTS,
                              max_len: Optional[int] = None) -> Optional[Dict[str, Any]]:
    logging.debug(f"get_concise_snippet_alias called with node_id={node_id}, topic={topic}, persona_or_none={persona_or_none}")
    eff_max_len = max_len if max_len is not None else max_chars
    return _strict_get_concise_snippet(
        node_id=node_id or "",
        topic=topic or "",
        persona=persona_or_none,
        max_len=eff_max_len,
        max_sents=max_sents,
        seed_keys=seed_keys
    )

# Public API that supports both positional and persona_or_none kw usage.
def get_concise_snippet(*args,
                        node_id: Optional[str] = None,
                        topic: Optional[str] = None,
                        persona: Optional[str] = None,
                        persona_or_none: Optional[str] = None,
                        seed_keys: Optional[Tuple[Any, ...]] = None,
                        max_chars: int = _A3_MAX_LEN,
                        max_sents: int = _A3_MAX_SENTS,
                        max_len: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    - Positional: get_concise_snippet("KB_QA", "general", "D", seed_keys=...)
    - Keyword: get_concise_snippet(node_id="KB_QA", topic="general", persona_or_none=None)
    - Back-compat: accepts max_len or max_chars; max_len takes precedence if provided.
    """
    logging.debug(f"get_concise_snippet called with args={args}, node_id={node_id}, topic={topic}, persona={persona}, persona_or_none={persona_or_none}")
    # Handle persona_or_none parameter for backward compatibility
    effective_persona = persona_or_none if persona_or_none is not None else persona
    eff_max_len = max_len if max_len is not None else max_chars
    
    # Positional path: get_concise_snippet("KB_QA", "general", "D", seed_keys=...)
    if len(args) >= 3:
        pos_node, pos_topic, pos_persona = args[:3]
        logging.debug(f"Positional path detected: node={pos_node}, topic={pos_topic}, persona={pos_persona}")
        return _strict_get_concise_snippet(
            node_id=str(pos_node or ""),
            topic=str(pos_topic or ""),
            persona=pos_persona if pos_persona in _A3_ALLOWED_PERSONAS or pos_persona is None else None,
            max_len=eff_max_len,
            max_sents=max_sents,
            seed_keys=seed_keys
        )
    
    # Keyword path
    eff_node = str(node_id or "")
    eff_topic = str(topic or "")
    eff_persona = effective_persona if effective_persona in _A3_ALLOWED_PERSONAS or effective_persona is None else None
    logging.debug(f"Keyword path detected: node={eff_node}, topic={eff_topic}, persona={eff_persona}")
    return _strict_get_concise_snippet(
        node_id=eff_node,
        topic=eff_topic,
        persona=eff_persona,
        max_len=eff_max_len,
        max_sents=max_sents,
        seed_keys=seed_keys
    )