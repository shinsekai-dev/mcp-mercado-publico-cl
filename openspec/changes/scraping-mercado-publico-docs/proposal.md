# Proposal: Scraping Mercado Público Documents

## Description

The official Mercado Público API (v1) provides comprehensive data about tenders (licitaciones) and purchase orders (órdenes de compra), but it lacks direct access to the downloadable documents (PDFs, DOCs, etc.) that are essential for background research and bidding processes. These documents are only available through the web portal using a series of dynamic interactions involving encrypted parameters and ASP.NET ViewState.

This change aims to bridge this gap by adding a scraping capability to the `mercado-publico` MCP server, allowing users to retrieve all downloadable document links for a specific tender code.

## Goals

- Implement a new MCP tool `obtener_documentos_licitacion` that takes a tender code (e.g., `1509-5-L114`) and returns a list of downloadable documents.
- Automate the multi-step navigation flow:
    1. Search for the tender code on the web portal to obtain internal IDs.
    2. Navigate to the tender details page to find attachment groups.
    3. Navigate to the attachment viewer to extract individual file download links.
- Minimize external dependencies by using `httpx` for the scraping logic if possible, or `playwright` if dynamic rendering proves too complex for static extraction.

## Requirements

- **Input**: A valid Mercado Público tender code string.
- **Output**: A collection of document objects containing:
    - `Nombre`: The filename.
    - `Descripcion`: Description of the document if available.
    - `UrlDescarga`: A direct link to download the document (or a proxied link if direct links are short-lived).
- **Resilience**: The scraper should handle ASP.NET's session management and ViewState requirements.

## Impact

- **New Infrastructure Component**: `MercadoPublicoScraper` to handle web-based retrieval.
- **New Use Case**: `ObtenerDocumentosLicitacion` in the application layer.
- **New MCP Tool**: `obtener_documentos_licitacion` exposed to the LLM.
- **Dependencies**: No change to the official API ticket/ticket requirement, as this uses the public search portal.
