"""Descargador de documentos desde Mercado Público."""

import asyncio
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import get_download_dir, ensure_dir

console = Console()


class DocumentDownloader:
    """
    Descarga documentos desde URLs usando httpx (sin sesion de navegador).

    DEPRECADO para URLs del portal Mercado Público: las URLs de VerAntecedentes.aspx
    requieren cookies de sesion ASP.NET. Usar MPBrowser.descargar_documentos_con_sesion()
    en su lugar.

    Este cliente sigue siendo util para descargas de recursos publicos que no requieren
    autenticacion (CDN, APIs abiertas, etc.).
    """

    def __init__(self, download_dir: Optional[Path] = None, timeout: int = 60, cookies: Optional[dict] = None):
        self.download_dir = download_dir or get_download_dir()
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            cookies=cookies or {},
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _extract_filename(
        self, url: str, response: httpx.Response, default_name: str = "documento"
    ) -> str:
        """Extrae el nombre del archivo de la URL o headers."""
        # Intentar obtener del header Content-Disposition
        content_disposition = response.headers.get("content-disposition", "")
        if "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip("\"'")
            return unquote(filename)

        # Intentar obtener del parámetro 'enc' en la URL
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "enc" in params:
            # El parámetro enc está encriptado, usamos un nombre generado
            pass

        # Intentar obtener de la URL path
        path = unquote(parsed.path)
        if "/" in path:
            filename = path.split("/")[-1]
            if filename and "." in filename:
                return filename

        # Si no hay nombre, usar el default con extensión del content-type
        content_type = response.headers.get("content-type", "")
        if "pdf" in content_type:
            return f"{default_name}.pdf"
        elif "word" in content_type or "msword" in content_type:
            return f"{default_name}.doc"
        elif "officedocument" in content_type:
            return f"{default_name}.docx"
        else:
            return f"{default_name}.bin"

    async def descargar_documento(
        self, url: str, nombre: str, output_dir: Path, sem: asyncio.Semaphore
    ) -> Optional[Path]:
        """
        Descarga un documento desde URL.

        Args:
            url: URL del documento
            nombre: Nombre descriptivo del documento
            output_dir: Directorio de salida
            sem: Semáforo para limitar concurrencia

        Returns:
            Path al archivo descargado o None si falló
        """
        async with sem:
            try:
                console.print(f"[dim]  [DOWN] Descargando: {nombre[:50]}...[/dim]")

                response = await self.client.get(url)
                response.raise_for_status()

                # Determinar nombre de archivo
                filename = self._extract_filename(
                    url, response, nombre.replace(" ", "_").lower()[:30]
                )
                filepath = output_dir / filename

                # Guardar archivo
                with open(filepath, "wb") as f:
                    f.write(response.content)

                console.print(
                    f"[green]  [OK][/green] {filename} ({len(response.content)} bytes)"
                )
                return filepath

            except Exception as e:
                console.print(f"[red]  [ERROR][/red] Error descargando {nombre}: {e}")
                return None

    async def descargar_documentos(
        self, documentos: list[dict], output_dir: Path, max_concurrent: int = 3
    ) -> list[Path]:
        """
        Descarga múltiples documentos con concurrencia controlada.

        Args:
            documentos: Lista de dicts con 'nombre' y 'url'
            output_dir: Directorio de salida
            max_concurrent: Máximo de descargas simultáneas

        Returns:
            Lista de paths a archivos descargados exitosamente
        """
        ensure_dir(output_dir)

        sem = asyncio.Semaphore(max_concurrent)
        tasks = [
            self.descargar_documento(doc["url"], doc["nombre"], output_dir, sem)
            for doc in documentos
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar solo los exitosos (Paths)
        exitosos = [r for r in results if isinstance(r, Path)]

        console.print(
            f"[green][OK][/green] Descargados {len(exitosos)}/{len(documentos)} documentos"
        )
        return exitosos
