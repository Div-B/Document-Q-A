-- Enable vector extension
create extension if not exists vector;

-- Documents table
create table documents (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamp with time zone default now()
);

-- Chunks table with vector column
create table chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade,
  content text not null,
  embedding vector(1536),
  page_number int,
  chunk_index int,
  created_at timestamp with time zone default now()
);

-- Index for fast similarity search
create index on chunks using ivfflat (embedding vector_cosine_ops);

-- Similarity search function
create or replace function match_chunks(
    query_embedding vector(1536),
    match_count int default 5
)
returns table(
    id uuid,
    document_id uuid,
    content text,
    page_number int,
    chunk_index int,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        chunks.id,
        chunks.document_id,
        chunks.content,
        chunks.page_number,
        chunks.chunk_index,
        1 - (chunks.embedding <=> query_embedding) as similarity
    from chunks
    order by chunks.embedding <=> query_embedding
    limit match_count;
end;
$$;