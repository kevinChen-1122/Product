from typing import List, Dict, Any

class Provider:
    name: str = "base"

    async def load(self) -> List[Dict[str, Any]]:
        """Return a list of configs. Each item must include at least:
        {
          "seller_id": "u_123",
          "keywords": [...],
          "filters": {...},
          "notification": {...}
        }
        """
        raise NotImplementedError
