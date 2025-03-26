from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.config import config
from app.utils.db import get_db, Database
from pathlib import Path
import os
import datetime

router = APIRouter()

class GeneratedFileInfo(BaseModel):
    """生成文件信息模型"""
    filename: str
    content_preview: str
    project: Optional[str] = None
    timestamp: Optional[str] = None


class GeneratedFilesResponse(BaseModel):
    """生成文件列表响应模型"""
    files: List[GeneratedFileInfo]


@router.get("/generated_files", response_model=GeneratedFilesResponse)
async def get_generated_files(
    project_id: Optional[str] = Query(None, description="项目ID（可选）"),
    db: Database = Depends(get_db)
):
    """
    获取模型生成的文件列表

    Args:
        project_id: 需要获取特定项目文件时的项目ID
        db: 数据库连接

    Returns:
        生成文件信息列表
    """
    try:
        files = []

        # 根据项目ID获取工作区路径
        workspace_path = config.get_workspace_path(project_id)

        # 工作区不存在时返回空列表
        if not workspace_path.exists():
            return {"files": []}

        # 遍历工作区文件
        for root, _, filenames in os.walk(workspace_path):
            for filename in filenames:
                try:
                    # 文件绝对路径
                    file_path = Path(root) / filename

                    # 相对于工作区根目录的路径
                    rel_path = file_path.relative_to(workspace_path)

                    # 文件修改时间
                    mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

                    # 跳过过大文件（可选配置）
                    if file_path.stat().st_size > 1024 * 1024:  # 跳过1MB以上文件
                        continue

                    # 文件内容预览处理
                    preview = ""
                    try:
                        # 二进制文件特殊处理
                        if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf', '.zip', '.exe']:
                            preview = "[二进制文件]"
                        else:
                            # 文本文件读取前200字符
                            with open(file_path, 'r', encoding='utf-8') as f:
                                preview = f.read(200)
                                if len(preview) == 200:
                                    preview += "..."
                    except UnicodeDecodeError:
                        # 编码错误视为二进制文件
                        preview = "[二进制文件]"
                    except Exception as e:
                        preview = f"[预览获取错误: {str(e)}]"

                    # 添加文件信息
                    files.append(
                        GeneratedFileInfo(
                            filename=str(rel_path),
                            content_preview=preview,
                            project=project_id,
                            timestamp=mtime
                        )
                    )
                except Exception as e:
                    # 单文件处理错误跳过
                    print(f"文件处理错误: {str(e)}")
                    continue

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取生成文件列表时发生错误: {str(e)}")