import logging
import re
import unicodedata

logger = logging.getLogger(__name__)

class TextCleaner:

    MIME_TO_TYPE = {
            "text/plain": "txt",
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        }
    
    def clean_text(self, text: str, file_type: str) -> str:
        """
        Cleans the extracted text by removing unwanted characters and formatting.
        """
        normalized_file_type = self.MIME_TO_TYPE.get(file_type)

        if normalized_file_type is None:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Add cleaning logic based on file type
        if normalized_file_type == "txt":
            logger.info("Cleaning text from .txt file.")
            return self._clean_txt(text)
        elif normalized_file_type == "pdf":
            logger.info("Cleaning text from .pdf file.")
            return self._clean_pdf(text)
        elif normalized_file_type == "docx":
            logger.info("Cleaning text from .docx file.")
            return self._clean_docx(text)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
    def _clean_txt(self, text: str) -> str:
        return self._generic_clean(text)
    
    def _clean_pdf(self, text: str) -> str:
        return self._generic_clean(text)
    
    def _clean_docx(self, text: str) -> str:
        return self._generic_clean(text)
    
    def _generic_clean(self, text: str) -> str:
        text = self._normalize_unicode(text)
        text = self._normalize_line_endings(text)
        text = self._remove_zero_width_characters(text)
        text = self._collapse_whitespace(text)
        text = self._collapse_blank_lines(text)
        text = self._strip(text)

        logger.info("Text cleaning completed.")
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)
    
    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")
    
    def _remove_zero_width_characters(self, text: str) -> str:
        return re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    
    def _collapse_whitespace(self, text: str) -> str:
        return re.sub(r"[ \t]+", " ", text)
    
    def _collapse_blank_lines(self, text: str) -> str:
        return re.sub(r"\n{2,}", "\n\n", text)
    
    def _strip(self, text: str) -> str:
        return text.strip()
    
    