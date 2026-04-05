# Specs: Document Tools

## Tool: `listar_documentos_licitacion`

### Description
Lists all downloadable documents for a given tender code, grouped by category.

### Requirements
- **Search**: Must resolve the tender code to a web portal `qs`.
- **Extraction**: Must find all attachment groups (`enc`) and files within them.
- **Output**: JSON schema with groups and document names.

---

## Tool: `leer_documento_licitacion`

### Description
Downloads and parses the text content of a specific PDF document from a tender.

### Requirements
- **Selection**: Must identify the correct document by name or ID within a tender.
- **Parsing**: Must extract text and tables, converting them to Markdown.
- **Output**: The extracted text context for the LLM.

## Scenarios

### Scenario: Full Context Retrieval
- **GIVEN** A tender code `1509-5-L114`.
- **WHEN** Calling `listar_documentos_licitacion`.
- **THEN** It returns a list of 5 documents.
- **WHEN** Calling `leer_documento_licitacion` for "Bases_Administrativas.pdf".
- **THEN** It returns the full text of the bases in Markdown, including table structures for items and requirements.

### Scenario: Scanned PDF No-Text
- **GIVEN** A document that is a scanned image without an OCR layer.
- **WHEN** `leer_documento_licitacion` is called.
- **THEN** It returns a message: "El documento es una imagen escaneada y no se pudo extraer texto. Por favor, revisa el archivo manualmente."
