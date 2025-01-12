"""プリセット機能を提供する API Router"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response

from voicevox_engine.preset.Preset import Preset
from voicevox_engine.preset.PresetError import PresetError
from voicevox_engine.preset.PresetManager import PresetManager

from ..dependencies import check_disabled_mutable_api


def generate_preset_router(preset_manager: PresetManager) -> APIRouter:
    """プリセット API Router を生成する"""
    router = APIRouter()

    @router.get(
        "/presets",
        response_model=list[Preset],
        response_description="プリセットのリスト",
        tags=["その他"],
    )
    def get_presets() -> list[Preset]:
        """
        エンジンが保持しているプリセットの設定を返します
        """
        try:
            presets = preset_manager.load_presets()
        except PresetError as err:
            raise HTTPException(status_code=422, detail=str(err))
        return presets

    @router.post(
        "/add_preset",
        response_model=int,
        response_description="追加したプリセットのプリセットID",
        tags=["その他"],
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    def add_preset(
        preset: Annotated[
            Preset,
            Body(
                description="新しいプリセット。プリセットIDが既存のものと重複している場合は、新規のプリセットIDが採番されます。"
            ),
        ]
    ) -> int:
        """
        新しいプリセットを追加します
        """
        try:
            id = preset_manager.add_preset(preset)
        except PresetError as err:
            raise HTTPException(status_code=422, detail=str(err))
        return id

    @router.post(
        "/update_preset",
        response_model=int,
        response_description="更新したプリセットのプリセットID",
        tags=["その他"],
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    def update_preset(
        preset: Annotated[
            Preset,
            Body(
                description="更新するプリセット。プリセットIDが更新対象と一致している必要があります。"
            ),
        ]
    ) -> int:
        """
        既存のプリセットを更新します
        """
        try:
            id = preset_manager.update_preset(preset)
        except PresetError as err:
            raise HTTPException(status_code=422, detail=str(err))
        return id

    @router.post(
        "/delete_preset",
        status_code=204,
        tags=["その他"],
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    def delete_preset(
        id: Annotated[int, Query(description="削除するプリセットのプリセットID")]
    ) -> Response:
        """
        既存のプリセットを削除します
        """
        try:
            preset_manager.delete_preset(id)
        except PresetError as err:
            raise HTTPException(status_code=422, detail=str(err))
        return Response(status_code=204)

    return router
