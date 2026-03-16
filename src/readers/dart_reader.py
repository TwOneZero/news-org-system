"""DART (Korean Disclosure System) reader for corporate disclosures."""

import os
from datetime import datetime, timedelta
from typing import List, Optional

import dart_fss

from .base_reader import BaseReader, Article


class DARTReader(BaseReader):
    """Reader for Korean DART (Data Analysis, Retrieval and Transfer System) disclosures.

    Fetches corporate disclosures from the Korean Electronic Disclosure System.
    Requires DART API key (available for free at https://opendart.fss.or.kr/).
    """

    def __init__(self, source_name: str = "dart", api_key: Optional[str] = None):
        """Initialize the DART reader.

        Args:
            source_name: Name identifier for this source
            api_key: DART API key (defaults to DART_API_KEY env variable)
        """
        super().__init__(source_name)
        self.api_key = api_key or os.getenv("DART_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DART API key required. Set DART_API_KEY environment variable "
                "or pass api_key parameter. Get free API key at "
                "https://opendart.fss.or.kr/"
            )

        # Initialize dart-fss with API key
        dart_fss.set_api_key(self.api_key)

    def fetch(
        self,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        corp_code: Optional[str] = None,
    ) -> List[Article]:
        """Fetch disclosures from DART.

        Args:
            limit: Maximum number of disclosures to fetch
            start_date: Filter disclosures filed after this date
            end_date: Filter disclosures filed before this date
            corp_code: Filter by specific corporation code (e.g., '005930' for Samsung)

        Returns:
            List of Article objects representing disclosures
        """
        articles = []

        # Default to last 7 days if no date range specified
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        try:
            # Search for disclosures
            search_results = dart_fss.api.filings.search_filings(
                bgn_de=start_date.strftime("%Y%m%d"),
                end_de=end_date.strftime("%Y%m%d"),
                corp_code=corp_code,
                page_count=limit or 10,
            )

            for filing in search_results.get("list", []):
                # Parse filing date
                rcept_dt = filing.get("rcept_dt")  # Receipt date
                if rcept_dt:
                    published_date = datetime.strptime(rcept_dt, "%Y%m%d")
                else:
                    published_date = datetime.now()

                # Extract disclosure content
                content = self._extract_disclosure_content(
                    filing.get("rcept_no"), filing.get("corp_code")
                )

                article = Article(
                    source=self.source_name,
                    url=f"https://dart.fss.or.kr/dsaf001/main.do?rceptNo={filing.get('rcept_no')}",
                    title=filing.get("report_nm", ""),
                    content=content,
                    published_at=published_date,
                    crawled_at=datetime.now(),
                    metadata={
                        "corp_code": filing.get("corp_code"),
                        "corp_name": filing.get("corp_name"),
                        "stock_code": filing.get("stock_code"),
                        "report_nm": filing.get("report_nm"),
                        "rcept_no": filing.get("rcept_no"),
                        "rm": filing.get("rm"),  # Reason for amendment (if any)
                    },
                )
                articles.append(article)

                # Check limit
                if limit and len(articles) >= limit:
                    break

        except Exception as e:
            print(f"Error fetching DART disclosures: {e}")

        return articles

    def _extract_disclosure_content(self, rcept_no: str, corp_code: str) -> str:
        """Extract full disclosure content.

        Args:
            rcept_no: Disclosure receipt number
            corp_code: Corporation code

        Returns:
            Extracted disclosure text
        """
        try:
            # Get disclosure document
            docs = dart_fss.api.filings.documents(rcept_no=rcept_no)

            if not docs:
                return ""

            # Extract text from available documents
            content_parts = []
            for doc in docs:
                content_parts.append(f"[{doc.get('title', '')}]")

            return "\n\n".join(content_parts)

        except Exception as e:
            print(f"Error extracting disclosure content: {e}")
            return ""

    def get_corp_code(self, corp_name: str) -> Optional[str]:
        """Get corporation code from corporation name.

        Args:
            corp_name: Corporation name (e.g., '삼성전자')

        Returns:
            Corporation code (e.g., '005930') or None if not found
        """
        try:
            corp_code = dart_fss.api.corp_code.find_corp_code_by_corp_name(
                corp_name=corp_name
            )
            return corp_code
        except Exception as e:
            print(f"Error finding corp code for {corp_name}: {e}")
            return None
