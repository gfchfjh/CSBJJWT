"""
频道映射API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import json
import io
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


@router.put("/{mapping_id}/toggle")
async def toggle_mapping(mapping_id: int):
    """启用/禁用频道映射"""
    try:
        # 获取当前映射
        mappings = db.get_channel_mappings()
        mapping = next((m for m in mappings if m['id'] == mapping_id), None)
        
        if not mapping:
            raise HTTPException(status_code=404, detail="映射不存在")
        
        # 切换状态
        new_enabled = 0 if mapping['enabled'] == 1 else 1
        
        # 更新数据库
        db.execute(
            "UPDATE channel_mappings SET enabled = ? WHERE id = ?",
            (new_enabled, mapping_id)
        )
        db.commit()
        
        return {"message": "状态已更新", "enabled": new_enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{mapping_id}")
async def delete_mapping(mapping_id: int):
    """删除频道映射"""
    try:
        db.execute("DELETE FROM channel_mappings WHERE id = ?", (mapping_id,))
        db.commit()
        return {"message": "映射已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_mappings():
    """导出所有频道映射为JSON文件"""
    try:
        mappings = db.get_channel_mappings()
        
        # 准备导出数据
        export_data = {
            "version": "1.0",
            "export_time": db.execute("SELECT datetime('now')").fetchone()[0],
            "mappings": [
                {
                    "kook_server_id": m['kook_server_id'],
                    "kook_channel_id": m['kook_channel_id'],
                    "kook_channel_name": m['kook_channel_name'],
                    "target_platform": m['target_platform'],
                    "target_bot_id": m['target_bot_id'],
                    "target_channel_id": m['target_channel_id'],
                    "enabled": m['enabled']
                }
                for m in mappings
            ]
        }
        
        # 生成JSON字符串
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # 创建文件流
        stream = io.BytesIO(json_str.encode('utf-8'))
        
        return StreamingResponse(
            stream,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=channel_mappings_export.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


class MappingImportRequest(BaseModel):
    mappings: List[MappingCreate]
    replace_existing: bool = False  # 是否替换现有映射


@router.post("/import")
async def import_mappings(request: MappingImportRequest):
    """导入频道映射（批量）"""
    try:
        success_count = 0
        failed_count = 0
        errors = []
        
        # 如果选择替换现有，先删除所有映射
        if request.replace_existing:
            db.execute("DELETE FROM channel_mappings")
            db.commit()
        
        # 批量添加映射
        for mapping_data in request.mappings:
            try:
                db.add_channel_mapping(
                    kook_server_id=mapping_data.kook_server_id,
                    kook_channel_id=mapping_data.kook_channel_id,
                    kook_channel_name=mapping_data.kook_channel_name,
                    target_platform=mapping_data.target_platform,
                    target_bot_id=mapping_data.target_bot_id,
                    target_channel_id=mapping_data.target_channel_id
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    "channel": mapping_data.kook_channel_name,
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "message": "导入完成",
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/import/file")
async def import_mappings_from_file(file: UploadFile = File(...)):
    """从JSON文件导入频道映射"""
    try:
        # 读取文件内容
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        # 验证文件格式
        if "mappings" not in data:
            raise HTTPException(status_code=400, detail="无效的文件格式：缺少mappings字段")
        
        # 转换为MappingCreate对象
        mappings = []
        for m in data["mappings"]:
            try:
                mappings.append(MappingCreate(
                    kook_server_id=m['kook_server_id'],
                    kook_channel_id=m['kook_channel_id'],
                    kook_channel_name=m['kook_channel_name'],
                    target_platform=m['target_platform'],
                    target_bot_id=m['target_bot_id'],
                    target_channel_id=m['target_channel_id']
                ))
            except KeyError as e:
                raise HTTPException(status_code=400, detail=f"映射数据缺少必要字段: {str(e)}")
        
        # 调用导入逻辑
        request = MappingImportRequest(mappings=mappings, replace_existing=False)
        return await import_mappings(request)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
