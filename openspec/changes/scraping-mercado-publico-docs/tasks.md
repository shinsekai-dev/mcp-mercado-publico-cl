# Tasks: Scraping & Reading Mercado Público Documents

## Phase 1: Infrastructure (Scraper & Parser)

- [ ] 1.1 Create `infrastructure/mercado_publico_scraper.py`
    - [ ] Implementation of `search_tender`, `get_attachment_groups`, `get_group_documents`.
    - [ ] Implementation of `download_document` (binary retrieval).
- [ ] 1.2 Create `infrastructure/document_parser.py`
    - [ ] Integrate `pdfplumber`.
    - [ ] Logic for text and table extraction to Markdown.

## Phase 2: Domain (Entities)

- [ ] 2.1 Update `domain/licitacion/entities.py`
    - [ ] Add `DocumentoLicitacion` (Name, ID, Category, Content).

## Phase 3: Application (Use Cases)

- [ ] 3.1 Create `application/licitacion/lista_documentos_licitacion.py`.
- [ ] 3.2 Create `application/licitacion/lee_documento_licitacion.py`.
- [ ] 3.3 Register use cases in `application/licitacion/use_cases.py`.

## Phase 4: Interfaces (MCP Tools)

- [ ] 4.1 Update `interfaces/mcp/tools.py`
    - [ ] Add `listar_documentos_licitacion(codigo: str)`.
    - [ ] Add `leer_documento_licitacion(codigo: str, nombre_documento: str)`.

## Phase 5: Verification

- [ ] 5.1 Unit tests for `DocumentParser` with sample PDF.
- [ ] 5.2 Manual verification of full flow with `1509-5-L114`.
- [ ] 5.3 Verify Markdown quality for LLM consumption.
