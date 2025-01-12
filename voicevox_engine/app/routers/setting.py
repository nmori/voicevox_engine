"""設定機能を提供する API Router"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.templating import Jinja2Templates

from voicevox_engine.engine_manifest.EngineManifest import EngineManifest
from voicevox_engine.setting.Setting import CorsPolicyMode, Setting
from voicevox_engine.setting.SettingLoader import SettingHandler

from ..dependencies import check_disabled_mutable_api


def generate_setting_router(
    setting_loader: SettingHandler,
    engine_manifest_data: EngineManifest,
    setting_ui_template: Jinja2Templates,
) -> APIRouter:
    """設定 API Router を生成する"""
    router = APIRouter()

    @router.get("/setting", response_class=Response, tags=["設定"])
    def setting_get(request: Request) -> Response:
        """
        設定ページを返します。
        """
        settings = setting_loader.load()

        brand_name = engine_manifest_data.brand_name
        cors_policy_mode = settings.cors_policy_mode
        allow_origin = settings.allow_origin

        if allow_origin is None:
            allow_origin = ""

        return setting_ui_template.TemplateResponse(
            "ui.html",
            {
                "request": request,
                "brand_name": brand_name,
                "cors_policy_mode": cors_policy_mode.value,
                "allow_origin": allow_origin,
            },
        )

    @router.post(
        "/setting",
        response_class=Response,
        tags=["設定"],
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    def setting_post(
        cors_policy_mode: Annotated[CorsPolicyMode, Form()],
        allow_origin: Annotated[str | None, Form()] = None,
    ) -> Response:
        """
        設定を更新します。
        """
        settings = Setting(
            cors_policy_mode=cors_policy_mode,
            allow_origin=allow_origin,
        )

        # 更新した設定へ上書き
        setting_loader.save(settings)

        return Response(status_code=204)

    return router
