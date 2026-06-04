from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.storage.service import gcs_service

router = APIRouter(prefix="/storage", tags=["Storage"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Tải tệp tin lên Google Cloud Storage. Trả về public URL truy cập tệp tin.
    """
    try:
        content = await file.read()
        file_url = gcs_service.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        return {
            "message": "Tải lên thành công",
            "file_url": file_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tải tệp lên GCS: {str(e)}"
        )

@router.delete("/delete")
async def delete_file(file_url: str):
    """
    Xóa tệp tin trên Google Cloud Storage bằng Public URL.
    """
    try:
        success = gcs_service.delete_file(file_url)
        if success:
            return {"message": "Xóa tệp tin thành công"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy tệp tin hoặc URL không hợp lệ"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa tệp: {str(e)}"
        )
