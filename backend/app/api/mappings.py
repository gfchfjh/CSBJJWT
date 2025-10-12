"""
频道映射API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..database import db


router = APIRouter(prefix="/api/mappings", tags=["mappings"])


class MappingCreate(BaseModel):
    kook_server_id: str
    kook_channel_id: str
    kook_channel_name: str
    target_platform: str
    target_bot_id: int
    target_channel_id: str


class MappingResponse(BaseModel):
    id: int
    kook_server_id: str
    kook_channel_id: str
    kook_channel_name: str
    target_platform: str
    target_bot_id: int
    target_channel_id: str
    enabled: int


@router.get("/", response_model=List[MappingResponse])
async def get_mappings(kook_channel_id: str = None):
    """获取频道映射列表"""
    mappings = db.get_channel_mappings(kook_channel_id)
    return mappings


@router.post("/", response_model=MappingResponse)
async def add_mapping(mapping: MappingCreate):
    """添加频道映射"""
    mapping_id = db.add_channel_mapping(
        kook_server_id=mapping.kook_server_id,
        kook_channel_id=mapping.kook_channel_id,
        kook_channel_name=mapping.kook_channel_name,
        target_platform=mapping.target_platform,
        target_bot_id=mapping.target_bot_id,
        target_channel_id=mapping.target_channel_id
    )
    
    # 返回映射信息
    mappings = db.get_channel_mappings()
    new_mapping = next((m for m in mappings if m['id'] == mapping_id), None)
    
    if not new_mapping:
        raise HTTPException(status_code=500, detail="添加映射失败")
    
    return new_mapping


@router.delete("/{mapping_id}")
async def delete_mapping(mapping_id: int):
    """删除频道映射"""
    # TODO: 实现删除逻辑
    return {"message": "映射已删除"}
