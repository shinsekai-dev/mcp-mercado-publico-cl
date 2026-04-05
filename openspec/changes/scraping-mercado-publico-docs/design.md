# Design: Scraping Mercado Público Documents

## Context

The `mercado-publico` MCP server currently uses the official ChileCompra API. This API does not provide binary/document downloads. The user needs these documents for full tender analysis. The web portal (`www.mercadopublico.cl`) provides these documents through a multi-step navigation flow.

## Architecture & Logic

### Component: `MercadoPublicoScraper` (Infrastructure)

A new scraper will manage the interaction with the Mercado Público web portal.

1.  **Stage 1: Search Bypass**
    -   **URL**: `https://www.mercadopublico.cl/Home/BusquedaLicitacion` (GET)
    -   **Logic**: Search for the tender code to extract the `qs` parameter from the list items.
    -   **Fallback**: If the direct details URL can be constructed from the code (unlikely, usually requires `qs`), the scraper will use the search results page.

2.  **Stage 2: Details Acquisition**
    -   **URL**: `https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?qs=[qs]` (GET)
    -   **Logic**: Parse the HTML to find all links targeting `VerAntecedentes.aspx?enc=...`. These represent groups of attachments (e.g., "Bases", "Anexos").

3.  **Stage 3: Attachments Viewer**
    -   **URL**: `https://www.mercadopublico.cl/Procurement/Modules/Attachment/VerAntecedentes.aspx?enc=[enc]` (GET)
    -   **Logic**: 
        -   Extract the `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, and other ASP.NET hidden fields.
        -   Identify document rows and their corresponding "Ver" buttons (triggering a POST).
        -   The button IDs usually follow the pattern `grdAttachment$ctlXX$grdIbtnView`.

4.  **Stage 4: Document Retrieval**
    -   **Action**: POST to index `VerAntecedentes.aspx?enc=[enc]` with form data:
        -   `__EVENTTARGET`: Empty or the button ID.
        -   `__VIEWSTATE`: Extracted from Stage 3.
        -   `button_identity.x`: e.g., 0.
        -   `button_identity.y`: e.g., 0.
    -   **Result**: Capture the `location` header or the binary response.

### Component: `DocumentParser` (Infrastructure)

A new utility to extract structured data from binary documents.
- **Dependency**: `pdfplumber` (selected for its superior table extraction capabilities, essential for quotation items).
- **Output**: Clean Markdown-formatted text that preserves table structures.

### Component: Application Use Cases

1.  **`ListarDocumentosLicitacion`**:
    - Input: `codigo_externo`.
    - Coordinates Stage 1-3 of the scraper.
    - Returns a list of `DocumentoLicitacion` (Metadata only: Name, ID).

2.  **`LeerDocumentoLicitacion`**:
    - Input: `codigo_externo`, `nombre_documento`.
    - Coordinates Stage 4 of the scraper to download the binary.
    - Uses `DocumentParser` to extract text.
    - Returns `DocumentoLicitacion` including the `Contenido` field.

## Key Design Decisions

- **Two-Stage Tooling**: We separate listing from reading content to avoid context window overflows. Large tenders can have dozens of documents.
- **Markdown Output**: We choose Markdown as the representation for extracted text to help the LLM identify headers, lists, and tables correctly.
- **Memory Management**: The scraper will avoid saving large files to disk, processing the stream directly with `pdfplumber` where possible.

## Risks / Trade-offs

- **Format Variety**: While most files are PDF, some may be `.doc`, `.xls`, or `.zip`. We will start with robust PDF support and return a "formato no soportado" message for others.
- **Scanned Documents**: PDFs that are purely images (scanned without OCR) will not be readable with `pdfplumber`. We will note this limitation in the tool response.
- **Table Complexity**: Complex nested tables in government documents can still be challenging to parse perfectly into Markdown.
