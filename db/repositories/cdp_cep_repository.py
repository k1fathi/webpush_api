from .base_repository import BaseRepository
from db.models.cdp import CDP
from db.models.cep import CEP
from typing import Dict, Any, Optional

class CDPRepository(BaseRepository[CDP]):
    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> Optional[CDP]:
        cdp_data = self.db.query(CDP).filter(CDP.user_id == user_id).first()
        if cdp_data:
            cdp_data.data.update(data)
            self.db.commit()
            return cdp_data
        return await self.create({"user_id": user_id, "data": data})

class CEPRepository(BaseRepository[CEP]):
    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> Optional[CEP]:
        cep_data = self.db.query(CEP).filter(CEP.user_id == user_id).first()
        if cep_data:
            cep_data.data.update(data)
            self.db.commit()
            return cep_data
        return await self.create({"user_id": user_id, "data": data})
