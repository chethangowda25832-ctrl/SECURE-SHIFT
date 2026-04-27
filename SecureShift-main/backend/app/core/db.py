"""
Database connection and operations using Supabase
"""
from app.core.config import settings
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class _PostgRESTAdapter:
    """Minimal Supabase-compatible client using raw postgrest, works with new sb_ keys."""
    def __init__(self, url: str, key: str):
        self._url = url.rstrip("/")
        self._key = key
        self._headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }

    def table(self, name: str):
        from postgrest import SyncPostgrestClient
        c = SyncPostgrestClient(
            f"{self._url}/rest/v1",
            headers=self._headers,
            schema="public",
        )
        return c.from_(name)


class SupabaseDB:
    """Supabase database client"""

    def __init__(self):
        self.client = None
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Supabase credentials not set — DB disabled")
            return
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        url = settings.SUPABASE_URL
        # Try official client first (works with legacy eyJ... keys)
        try:
            from supabase import create_client
            self.client = create_client(url, key)
            logger.info("Supabase client initialized (official)")
            return
        except Exception as e:
            logger.warning(f"Official supabase client failed ({e}), using postgrest adapter")
        # Fallback: raw postgrest adapter (works with new sb_ keys)
        self.client = _PostgRESTAdapter(url, key)
        logger.info("Supabase client initialized (postgrest adapter)")

    def create_user(self, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = self.client.table("users").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def create_repository(self, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = self.client.table("repositories").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return None

    def get_repository(self, repo_id: str) -> Optional[Dict]:
        try:
            response = self.client.table("repositories").select("*").eq("id", repo_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            return None

    def list_repositories(self, user_id: Optional[str] = None) -> List[Dict]:
        try:
            query = self.client.table("repositories").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.order("created_at", desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return []

    def create_scan(self, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = self.client.table("scans").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            return None

    def get_scan(self, scan_id: str) -> Optional[Dict]:
        try:
            response = self.client.table("scans").select("*").eq("id", scan_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting scan: {e}")
            return None

    def update_scan(self, scan_id: str, data: Dict[str, Any]) -> bool:
        try:
            self.client.table("scans").update(data).eq("id", scan_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating scan: {e}")
            return False

    def create_vulnerability(self, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = self.client.table("vulnerabilities").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating vulnerability: {e}")
            return None

    def get_vulnerabilities(self, scan_id: str) -> List[Dict]:
        try:
            response = self.client.table("vulnerabilities").select("*").eq("scan_id", scan_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting vulnerabilities: {e}")
            return []

    def create_ai_fix(self, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = self.client.table("ai_fixes").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating AI fix: {e}")
            return None

    def get_ai_fixes(self, vulnerability_id: str) -> List[Dict]:
        try:
            response = self.client.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting AI fixes: {e}")
            return []

    def create_scan_log(self, scan_id: str, message: str, level: str = "info") -> bool:
        try:
            self.client.table("scan_logs").insert({
                "scan_id": scan_id,
                "log_message": message,
                "log_level": level
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error creating scan log: {e}")
            return False


# Global database instance
db = SupabaseDB()


def get_database() -> SupabaseDB:
    return db
