import logging
from docx import Document
from io import BytesIO
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

class TextExtractor:

    MIME_TO_TYPE = {
            "text/plain": "txt",
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        }
    
    def __init__(self):
        pass

    def _extract_txt(self, file_bytes: bytes) -> str:
        """
        Extract text from a .txt file.
        """
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError as exc:
            logger.exception(
                "Failed to extract text from .txt file."
            )
            raise RuntimeError(
                "Text extraction from .txt file failed."
            ) from exc

    def _extract_pdf(self, file_bytes: bytes) -> str:
        """
        Extract text from a .pdf file.
        """
        try:

            pdf_reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()

        except Exception as exc:
            logger.exception(
                "Failed to extract text from .pdf file."
            )
            raise RuntimeError(
                "Text extraction from .pdf file failed."
            ) from exc

    def _extract_docx(self, file_bytes: bytes) -> str:
        """
        Extract text from a .docx file.
        """
        try:
            
            doc = Document(BytesIO(file_bytes))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text.strip()
        except Exception as exc:
            logger.exception(
                "Failed to extract text from .docx file."
            )
            raise RuntimeError(
                "Text extraction from .docx file failed."
            ) from exc
        

    def extract(
            self,
            file_bytes: bytes,
            file_type: str,
    ) -> str:
        """
        Extracts text from a file based on its type.
        """

        normalized_file_type = self.MIME_TO_TYPE.get(file_type)

        if normalized_file_type is None:
            raise ValueError(f"Unsupported file type: {file_type}")

        if normalized_file_type == "txt":
            logger.info(
                "Extracting text from .txt file."
            )
            return self._extract_txt(file_bytes)
        
        elif normalized_file_type == "pdf":
            logger.info(
                "Extracting text from .pdf file."
            )
            return self._extract_pdf(file_bytes)

        elif normalized_file_type == "docx":
            logger.info(
                "Extracting text from .docx file."
            )
            return self._extract_docx(file_bytes)
        
        raise ValueError(f"Unsupported file type: {file_type}")