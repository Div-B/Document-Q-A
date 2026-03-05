# Technical Decision Log

A record of key technical decisions made during development and the reasoning behind them.

---

## 1. Why RAG instead of fine-tuning?

**Decision:** Use RAG (Retrieval Augmented Generation) instead of fine tuning a model on documents.

**Reasoning:**
- Fine-tuning is expensive, slow, and requires retraining every time documents change
- RAG works with any documents dynamically, no retraining needed
- RAG is more transparent you can show users exactly which passages the answer came from
- RAG is the industry standard pattern for document Q&A applications

---

## 2. Why chunk size 500 words with 50 word overlap?

**Decision:** Split documents into 500 word chunks with 50 word overlap between consecutive chunks.

**Reasoning:**
- Too small (< 100 words): chunks lack enough context for meaningful answers
- Too large (> 1000 words): sending too much irrelevant text to the LLM reduces answer quality and increases cost
- 500 words hits enough context without noise for most cases.
- 50 word overlap (10% of chunk size) ensures sentences split at boundaries still appear complete in at least one chunk
- Although depending on the type of documents the chunk size and overlap can be modified to be more efficient or include more context if needed.

---

## 3. Why pgvector instead of Pinecone?

**Decision:** Use Supabase with pgvector for vector storage instead of a dedicated vector database like Pinecone.

**Reasoning:**
- pgvector lives in the same PostgreSQL database as our other data — simpler architecture, one less service to manage
- Supabase has a generous free tier covering both relational data and vector storage
- For the scale of this project pgvector performance is more than sufficient
- Pinecone would be worth considering at larger scale (millions of vectors)

---

## 4. Why asyncio.to_thread for Supabase?

**Decision:** Use `asyncio.to_thread` to run the synchronous Supabase client in a thread pool.

**Reasoning:**
- The Supabase Python client is synchronous — calling it directly in an async FastAPI route blocks the event loop
- Blocking the event loop prevents FastAPI from handling other requests concurrently
- `asyncio.to_thread` offloads the blocking call to a thread pool, keeping the event loop free
- The async Supabase client had connection stability issues on multiple sequential requests

---

## 5. Why stream the answer instead of waiting for the full response?

**Decision:** Stream GPT 4o responses token by token using Server Sent Events.

**Reasoning:**
- GPT 4o takes 5 to15 seconds to generate a full response
- Without streaming users stare at a blank screen
- Streaming shows progress immediately, making the app feel fast even on slow responses
- Token by token streaming is the industry standard for LLM applications

---

## 6. Why validate files on both frontend and backend?

**Decision:** Validate file type and size on both the React frontend and the FastAPI backend.

**Reasoning:**
- Frontend validation provides instant feedback without a network round trip
- Frontend validation can be bypassed by anyone sending raw HTTP requests directly to the API
- Backend validation is the only security critical check it cannot be bypassed
- Defense in depth: both layers working together gives the best user experience and security

---

## 7. Why rate limit by IP instead of by user?

**Decision:** Rate limit API endpoints by IP address rather than by authenticated user.

**Reasoning:**
- The app doesn't have user authentication yet
- IP based rate limiting is simple to implement and protects against accidental or malicious API abuse
- It prevents a single client from running up OpenAI API costs
- Limitation: shared IPs (offices, universities) could hit limits — acceptable tradeoff for now