import shutil
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from run import generate_app

from voicevox_engine.core.core_initializer import initialize_cores
from voicevox_engine.preset.PresetManager import PresetManager
from voicevox_engine.setting.SettingLoader import SettingHandler
from voicevox_engine.tts_pipeline.tts_engine import make_tts_engines_from_cores
from voicevox_engine.utility.core_version_utility import get_latest_version


@pytest.fixture()
def app_params(tmp_path: Path) -> dict[str, Any]:
    cores = initialize_cores(use_gpu=False, enable_mock=True)
    tts_engines = make_tts_engines_from_cores(cores)
    latest_core_version = get_latest_version(list(tts_engines.keys()))
    setting_loader = SettingHandler(Path("./not_exist.yaml"))

    # 隔離されたプリセットの生成
    original_preset_path = Path("./presets.yaml")
    preset_path = tmp_path / "presets.yaml"
    shutil.copyfile(original_preset_path, preset_path)
    preset_manager = PresetManager(preset_path)

    return {
        "tts_engines": tts_engines,
        "cores": cores,
        "latest_core_version": latest_core_version,
        "setting_loader": setting_loader,
        "preset_manager": preset_manager,
    }


@pytest.fixture()
def app(app_params: dict) -> FastAPI:
    return generate_app(**app_params)


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
