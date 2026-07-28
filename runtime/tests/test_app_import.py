def test_app_import_does_not_require_voicehub():
    from voxd.main import create_app

    app = create_app()

    assert app.title == "Voxd Runtime"
    assert app.version == "1.4.0"


def test_app_mounts_without_built_web_assets():
    from voxd.main import create_app

    app = create_app()

    assert app is not None
